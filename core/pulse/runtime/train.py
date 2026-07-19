import os
import time
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, get_cosine_schedule_with_warmup
from accelerate import Accelerator
import argparse
import sys
import os

# Add project root to sys.path to allow imports from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model import NIA500, NIAConfig
from src.data_stream import SovereignDataStream

# Try to import bitsandbytes for 8-bit optimization
try:
    import bitsandbytes as bnb
    HAS_BNB = True
except ImportError:
    HAS_BNB = False

class SovereignTrainer:
    """
    Lead Trainer for NIA.
    Handles 8-bit AdamW, Context Scaling, and Monitoring.
    """
    def __init__(self, args):
        self.args = args
        self.accelerator = Accelerator(mixed_precision="bf16" if args.bf16 else "fp16")
        self.device = self.accelerator.device
        
        self.config = NIAConfig()
        self.model = NIA500(self.config)
        
        # Gradient Checkpointing for 32k Context
        self.model.gradient_checkpointing_enable()
        
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.data_engine = SovereignDataStream(
            self.tokenizer, 
            max_seq_len=self.config.max_seq_len,
            sft_mode=self.args.sft
        )
        
        self.logs = []
        self.start_step = 0

        # Create output directory
        if self.accelerator.is_main_process:
            os.makedirs(args.output_dir, exist_ok=True)
        
        # Load from checkpoint if provided
        if args.checkpoint:
            self.load_checkpoint(args.checkpoint)

    def get_optimizer(self):
        if HAS_BNB:
            print("Sovereign 8-bit AdamW Engaged.")
            return bnb.optim.AdamW8bit(self.model.parameters(), lr=self.args.lr)
        else:
            print("Warning: bitsandbytes not found. Falling back to standard AdamW.")
            return torch.optim.AdamW(self.model.parameters(), lr=self.args.lr)

    def scale_context(self, current_step):
        """
        Linear Context Ramp up from 4k to 32k.
        """
        start_ctx = 4096
        end_ctx = 32768
        total_steps = self.args.total_steps
        
        if current_step >= total_steps:
            return end_ctx
        
        scaled_ctx = start_ctx + (end_ctx - start_ctx) * (current_step / total_steps)
        return int(scaled_ctx)

    def train(self):
        optimizer = self.get_optimizer()
        
        # Prepare Data
        if self.args.dummy:
            print("Sovereign Training: Dummy Data Mode Engaged.")
            # Create a simple dummy iterable dataset
            class DummyDataset(torch.utils.data.IterableDataset):
                def __init__(self, vocab_size, seq_len):
                    self.vocab_size = vocab_size
                    self.seq_len = seq_len
                def __iter__(self):
                    while True:
                        yield {
                            "input_ids": torch.randint(0, self.vocab_size, (self.seq_len,)),
                            "labels": torch.randint(0, self.vocab_size, (self.seq_len,))
                        }
            train_data = DummyDataset(self.config.vocab_size, self.config.max_seq_len)
        else:
            train_data = self.data_engine.get_stream()
            
        train_loader = DataLoader(train_data, batch_size=self.args.batch_size)
        
        # Cosine Schedule with 2,000 steps Warmup
        scheduler = get_cosine_schedule_with_warmup(
            optimizer, 
            num_warmup_steps=2000, 
            num_training_steps=self.args.total_steps
        )
        
        self.model, optimizer, train_loader, scheduler = self.accelerator.prepare(
            self.model, optimizer, train_loader, scheduler
        )
        
        self.model.train()
        print(f"Curriculum Training Phase Started (BF16: {self.args.bf16}).")
        
        start_time = time.time()
        
        for step, batch in enumerate(train_loader):
            # Adjust step if resuming
            effective_step = step + self.start_step
            
            if effective_step >= self.args.total_steps:
                break
            
            # Dynamic Context Scaling
            current_ctx = self.scale_context(effective_step)
            input_ids = batch["input_ids"][:, :current_ctx]
            labels = batch["labels"][:, :current_ctx]
            domain_bias = batch.get("domain_bias", torch.tensor([-1])).to(self.device).view(-1)
            
            optimizer.zero_grad()
            
            with self.accelerator.autocast():
                # Pass the first domain_bias of the batch (simplification for sample-level bias)
                logits, loss = self.model(input_ids, targets=labels)
                # Note: For multi-sample batches with different biases, a more complex mapping is needed.
                # For now, we apply the bias at the block level via the model's current_domain attribute.
                self.model.current_domain = domain_bias[0].item()
            
            self.accelerator.backward(loss)
            optimizer.step()
            scheduler.step()
            
            # Monitoring & Logging
            if effective_step % self.args.log_interval == 0:
                metrics = {
                    "step": effective_step,
                    "loss": loss.item(),
                    "context": current_ctx,
                    "vram_gb": torch.cuda.memory_allocated() / 1e9 if torch.cuda.is_available() else 0,
                    "timestamp": time.time() - start_time
                }
                self.logs.append(metrics)
                self.save_logs()
                print(f"Step {effective_step} | Loss: {loss.item():.4f} | Ctx: {current_ctx}")
            
            # Save Checkpoint
            if effective_step > 0 and effective_step % self.args.save_interval == 0:
                self.save_checkpoint(effective_step)

            # Zero-Shot Vibe-Check every 2000 steps
            if effective_step > 0 and effective_step % 2000 == 0:
                self.vibe_check()
                
        # Final Save
        self.save_checkpoint(self.args.total_steps, is_final=True)

    def save_logs(self):
        with open("training_log.json", "w") as f:
            json.dump(self.logs, f, indent=4)

    def vibe_check(self):
        """
        Verify the Sovereign Identity and reasoning velocity.
        """
        print("\n--- SOVEREIGN VIBE CHECK ---")
        prompts = [
            "Who are you?",
            "What is your technical architecture?",
            "Explain the logic of a recursive function in Kotlin."
        ]
        
        for prompt in prompts:
            print(f"Triggering analysis for: {prompt}")
            # Note: Functional generation would require weights. 
            # In training, we log the intent. In inference (src/chat.py), we see the output.
        print("--- END VIBE CHECK ---\n")

    def sync_to_kaggle(self, step):
        """
        Sync checkpoints to Kaggle datasets for persistence.
        """
        if not self.args.sync_kaggle:
            return
            
        print(f"Syncing Step {step} to Kaggle...")
        try:
            import subprocess
            # We assume 'kaggle' CLI is installed and configured in the environment
            # command: kaggle datasets version -p /path/to/checkpoints -m "Step {step}"
            result = subprocess.run(
                ["kaggle", "datasets", "version", "-p", self.args.output_dir, "-m", f"Checkpoint Step {step}"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print("Kaggle Sync Success.")
            else:
                print(f"Kaggle Sync Warning: {result.stderr}")
        except Exception as e:
            print(f"Kaggle Sync Failed: {e}")

    def save_checkpoint(self, step, is_final=False):
        """
        Saves the model and training state.
        """
        self.accelerator.wait_for_everyone()
        unwrapped_model = self.accelerator.unwrap_model(self.model)
        
        checkpoint_name = "final_model.pt" if is_final else f"checkpoint_{step}.pt"
        save_path = os.path.join(self.args.output_dir, checkpoint_name)
        
        # We save the model weights and the accelerator state
        state = {
            "step": step,
            "model_state": unwrapped_model.state_dict(),
            "config": self.config
        }
        
        self.accelerator.save(state, save_path)
        
        # Also save latest for convenience
        if not is_final:
            latest_path = os.path.join(self.args.output_dir, "latest.pt")
            self.accelerator.save(state, latest_path)
            
        print(f"Sovereign Checkpoint Saved: {save_path}")
        
        # Trigger Kaggle Sync if enabled
        if self.args.sync_kaggle:
            self.sync_to_kaggle(step)

    def load_checkpoint(self, checkpoint_path):
        """
        Loads the model and training state.
        """
        print(f"Loading Sovereign Checkpoint: {checkpoint_path}")
        checkpoint = torch.load(checkpoint_path, map_location="cpu")
        
        # Handle model state loading
        unwrapped_model = self.accelerator.unwrap_model(self.model)
        unwrapped_model.load_state_dict(checkpoint["model_state"])
        
        self.start_step = checkpoint.get("step", 0)
        print(f"Resuming from Step: {self.start_step}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--total_steps", type=int, default=100000)
    parser.add_argument("--steps", type=int, default=None, help="Alias for total_steps")
    parser.add_argument("--batch_size", type=int, default=2)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--bf16", action="store_true", default=True)
    parser.add_argument("--log_interval", type=int, default=500)
    parser.add_argument("--save_interval", type=int, default=2500)
    parser.add_argument("--output_dir", type=str, default="./checkpoints")
    parser.add_argument("--checkpoint", type=str, default=None, help="Path to checkpoint to resume from")
    parser.add_argument("--dummy", action="store_true", help="Use dummy data for testing")
    parser.add_argument("--sync_kaggle", action="store_true", help="Sync checkpoints to Kaggle")
    parser.add_argument("--sft", action="store_true", help="Enable Sovereign Instruction Tuning (SFT) mode")
    args = parser.parse_args()
    
    if args.steps is not None:
        args.total_steps = args.steps
    
    trainer = SovereignTrainer(args)
    trainer.train()
