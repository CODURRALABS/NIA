import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional, Tuple, Any, List

class NIAConfig:
    def __init__(self):
        self.d_model = 1024
        self.num_layers = 12
        self.num_heads = 16
        self.num_kv_heads = 4 # GQA 4:1
        self.d_ff = 2048 # Expert internal dimension
        self.num_experts = 8
        self.top_k = 2
        self.vocab_size = 50257
        self.max_seq_len = 32768
        self.rope_base = 1000000 # Increased for 32k context
        self.dropout = 0.1
        self.norm_eps = 1e-5

def precompute_rope_frequencies(dim: int, seq_len: int, base: float = 10000.0, device: str = "cpu"):
    """
    Precompute sin/cos frequencies for RoPE.
    """
    inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float().to(device) / dim))
    t = torch.arange(seq_len, device=device).float()
    freqs = torch.outer(t, inv_freq)
    emb = torch.cat((freqs, freqs), dim=-1)
    return emb.cos(), emb.sin()

def apply_rope(x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor):
    """
    Apply Rotary Positional Embeddings to x.
    """
    # x: [batch, num_heads, seq_len, head_dim]
    d = x.shape[-1]
    x1 = x[..., :d//2]
    x2 = x[..., d//2:]
    rotated_x = torch.cat((-x2, x1), dim=-1)
    return x * cos + rotated_x * sin

class SovereignExpert(nn.Module):
    """
    Logic-dense specialized expert module.
    """
    def __init__(self, config: NIAConfig):
        super().__init__()
        self.w1 = nn.Linear(config.d_model, config.d_ff, bias=False)
        self.w2 = nn.Linear(config.d_ff, config.d_model, bias=False)
        self.activation = nn.GELU()
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Activation and dropout as usual
        return self.w2(self.dropout(self.activation(self.w1(x))))

    def to_mmap(self):
        """
        Structural hook for memory-mapped weight offloading.
        In inference, weights will be paged in from disk on demand.
        """
        pass

class Top2Router(nn.Module):
    """
    Sovereign Top-2 Gating Network.
    """
    def __init__(self, config: NIAConfig):
        super().__init__()
        self.gate = nn.Linear(config.d_model, config.num_experts, bias=False)
        self.top_k = config.top_k

    def forward(self, x: torch.Tensor, domain_bias: int = -1) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        logits = self.gate(x)
        
        # Domain-Aware Biasing (Claude-Class Sonnet/Opus logic)
        # 0: Code Domain (Expert 0-3), 1: Logic Domain (Expert 4-7)
        if domain_bias == 0:
            logits[:, 4:] -= 10.0 # Suppress Logic Experts
        elif domain_bias == 1:
            logits[:, :4] -= 10.0 # Suppress Code Experts
            
        probs = F.softmax(logits, dim=-1)
        weights, indices = torch.topk(probs, self.top_k, dim=-1)
        # Re-normalize weights
        weights = weights / weights.sum(dim=-1, keepdim=True)
        return weights, indices, probs

class SparseMoE(nn.Module):
    """
    Sparse Mixture of Experts Layer.
    """
    def __init__(self, config: NIAConfig):
        super().__init__()
        self.experts = nn.ModuleList([SovereignExpert(config) for _ in range(config.num_experts)])
        self.router = Top2Router(config)
        self.num_experts = config.num_experts

    def forward(self, x: torch.Tensor, domain_bias: int = -1) -> Tuple[torch.Tensor, torch.Tensor]:
        batch, seq_len, d_model = x.shape
        x_flat = x.view(-1, d_model)
        
        # Explicitly typing weights and indices for the linter
        router_out: Tuple[torch.Tensor, torch.Tensor, torch.Tensor] = self.router(x_flat, domain_bias)
        weights, indices, gate_probs = router_out
        final_output: torch.Tensor = torch.zeros_like(x_flat)
        
        # Expert Parallel dispatching
        for i in range(self.num_experts):
            # indices: [batch * seq_len, top_k]
            # Find tokens that dispatch to expert i
            expert_mask: torch.Tensor = (indices == i) 
            if torch.any(expert_mask):
                # Get the tokens that require expert i
                token_mask: torch.Tensor = torch.any(expert_mask, dim=-1)
                token_indices: torch.Tensor = torch.where(token_mask)[0]
                
                # Get the specific weights for expert i at these tokens
                expert_weights_mask: torch.Tensor = (indices[token_indices] == i)
                # Sum weights across top-k if same expert is chosen twice
                token_expert_weights: torch.Tensor = (weights[token_indices] * expert_weights_mask.float()).sum(dim=-1, keepdim=True)
                
                # Dispatch to expert
                expert: SovereignExpert = self.experts[i]
                
                # EXPERT CHUNK PAGING (Structural Placeholder)
                # In production, this call would trigger an mmap-in if the expert is offloaded.
                expert_out: torch.Tensor = expert(x_flat[token_indices])
                
                final_output[token_indices] += token_expert_weights * expert_out

        return final_output.view(batch, seq_len, d_model), gate_probs

class GroupedQueryAttention(nn.Module):
    """
    GQA implementation for inference efficiency.
    """
    def __init__(self, config: NIAConfig):
        super().__init__()
        self.num_heads = config.num_heads
        self.num_kv_heads = config.num_kv_heads
        self.head_dim = config.d_model // config.num_heads
        self.kv_group_size = self.num_heads // self.num_kv_heads
        
        self.q_proj = nn.Linear(config.d_model, config.num_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(config.d_model, self.num_kv_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(config.d_model, self.num_kv_heads * self.head_dim, bias=False)
        self.o_proj = nn.Linear(config.num_heads * self.head_dim, config.d_model, bias=False)
        
        self.scale = self.head_dim ** -0.5

    def forward(self, x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        batch, seq_len, _ = x.shape
        
        q = self.q_proj(x).view(batch, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(batch, seq_len, self.num_kv_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(batch, seq_len, self.num_kv_heads, self.head_dim).transpose(1, 2)
        
        # Apply RoPE
        q = apply_rope(q, cos[:, :, :seq_len, :], sin[:, :, :seq_len, :])
        k = apply_rope(k, cos[:, :, :seq_len, :], sin[:, :, :seq_len, :])
        
        # GQA: Repeat K and V heads
        k = torch.repeat_interleave(k, self.kv_group_size, dim=1)
        v = torch.repeat_interleave(v, self.kv_group_size, dim=1)
        
        # Scaled Dot-Product Attention
        attn_weights = (q @ k.transpose(-2, -1)) * self.scale
        if mask is not None:
            attn_weights += mask
        attn_weights = F.softmax(attn_weights, dim=-1)
        
        out = (attn_weights @ v).transpose(1, 2).reshape(batch, seq_len, -1)
        return self.o_proj(out)

class NIA500Block(nn.Module):
    """
    Sovereign Transformer Block combining GQA and MoE.
    """
    def __init__(self, config: NIAConfig):
        super().__init__()
        self.ln1 = nn.LayerNorm(config.d_model, eps=config.norm_eps)
        self.attn = GroupedQueryAttention(config)
        self.ln2 = nn.LayerNorm(config.d_model, eps=config.norm_eps)
        self.moe = SparseMoE(config)

    def forward(self, x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor, mask: Optional[torch.Tensor] = None, domain_bias: int = -1) -> Tuple[torch.Tensor, torch.Tensor]:
        attn_out: torch.Tensor = self.attn(self.ln1(x), cos, sin, mask)
        h: torch.Tensor = x + attn_out
        moe_ln: torch.Tensor = self.ln2(h)
        moe_tuple: Tuple[torch.Tensor, torch.Tensor] = self.moe(moe_ln, domain_bias)
        moe_out, gate_probs = moe_tuple
        return h + moe_out, gate_probs

class NIA500(nn.Module):
    """
    NIA: The Sovereign Core.
    """
    def __init__(self, config: NIAConfig):
        super().__init__()
        self.config = config
        self.embeddings = nn.Embedding(config.vocab_size, config.d_model)
        
        self.blocks = nn.ModuleList([NIA500Block(config) for _ in range(config.num_layers)])
        self.norm = nn.LayerNorm(config.d_model, eps=config.norm_eps)
        self.head = nn.Linear(config.d_model, config.vocab_size, bias=False)
        
        self.gradient_checkpointing = False
        
        # Precompute RoPE
        cos, sin = precompute_rope_frequencies(
            config.d_model // config.num_heads, 
            config.max_seq_len, 
            config.rope_base
        )
        self.register_buffer("cos", cos.view(1, 1, config.max_seq_len, -1))
        self.register_buffer("sin", sin.view(1, 1, config.max_seq_len, -1))

    def gradient_checkpointing_enable(self, **kwargs):
        """
        Enables gradient checkpointing for memory-efficient training.
        """
        self.gradient_checkpointing = True

    def forward(self, input_ids: torch.Tensor, targets: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        batch, seq_len = input_ids.shape
        x = self.embeddings(input_ids)
        
        # Causal mask
        mask = torch.full((seq_len, seq_len), float("-inf"), device=input_ids.device)
        mask = torch.triu(mask, diagonal=1).view(1, 1, seq_len, seq_len)
        
        all_gate_probs = []
        for block in self.blocks:
            # We assume domain_bias is handled at the model level if passed
            domain_bias = getattr(self, "current_domain", -1)
            
            if self.gradient_checkpointing and self.training:
                def create_custom_forward(module):
                    def custom_forward(*inputs):
                        return module(*inputs)
                    return custom_forward
                
                x, gate_probs = torch.utils.checkpoint.checkpoint(
                    create_custom_forward(block),
                    x, self.cos, self.sin, mask, domain_bias,
                    use_reentrant=False
                )
            else:
                x, gate_probs = block(x, self.cos, self.sin, mask, domain_bias)
            
            all_gate_probs.append(gate_probs)
            
        x = self.norm(x)
        logits = self.head(x)
        
        loss = None
        if targets is not None:
            shift_logits = logits[:, :-1, :].contiguous()
            shift_targets = targets[:, 1:].contiguous()
            loss = F.cross_entropy(shift_logits.view(-1, self.config.vocab_size), shift_targets.view(-1))
            
            # Load-balancing loss
            avg_probs = torch.stack(all_gate_probs).mean(dim=(0, 1))
            aux_loss = self.config.num_experts * torch.sum(avg_probs**2) - 1
            loss += 0.01 * aux_loss
            
        return logits, loss

if __name__ == "__main__":
    config = NIAConfig()
    model = NIA500(config)
    params = sum(p.numel() for p in model.parameters())
    print(f"NIA Architecture Initialized (Gentleman).")
    print(f"Total Parameters: {params / 1e6:.2f}M")
    
    # Birth Test
    import time
    dummy_input = torch.randint(0, config.vocab_size, (1, 512))
    
    # Warmup
    with torch.no_grad():
        _ = model(dummy_input)
    
    start_time = time.time()
    with torch.no_grad():
        logits, _ = model(dummy_input)
    end_time = time.time()
    
    print(f"Forward Pass Successful. Output Shape: {logits.shape}")
    print(f"Processing Time (512 tokens): {(end_time - start_time) * 1000:.2f}ms")
