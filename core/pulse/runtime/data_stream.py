import torch
from datasets import load_dataset, interleave_datasets, IterableDataset
from transformers import AutoTokenizer
import random
import os
import sys

# Add parent directory to sys.path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SovereignDataStream:
    """
    High-velocity data engine for NIA training.
    Interleaves reasoning, coding, and identity datasets in streaming mode.
    """
    def __init__(self, tokenizer, max_seq_len=32768, shuffle_buffer=10000, sft_mode=False):
        self.tokenizer = tokenizer
        self.max_seq_len = max_seq_len
        self.shuffle_buffer = shuffle_buffer
        self.sft_mode = sft_mode
        
        # Dataset Configuration with Weightage
        # Total: 100% (40% Reasoning, 40% Coding, 20% Identity/General)
        if sft_mode:
            self.config = {
                "instruction": [
                    {"path": "data/instruction_tuning.jsonl", "weight": 1.0}
                ]
            }
        else:
            self.config = {
                "reasoning": [
                    {"path": "HuggingFaceFW/fineweb-edu", "subset": "default", "weight": 0.20},
                    {"path": "Open-Orca/OpenOrca", "subset": "default", "weight": 0.10},
                    {"path": "microsoft/orca-math-word-problems-200k", "subset": "default", "weight": 0.05},
                ],
                "coding": [
                    {"path": "bigcode/starcoderdata", "subset": "default", "weight": 0.20},
                    {"path": "m-a-p/CodeFeedback-Filtered-Instruction", "subset": "default", "weight": 0.10},
                    {"path": "ise-uiuc/Magicoder-OSS-Instruct-75K", "subset": "default", "weight": 0.10},
                ],
                "identity": [
                    {"path": "data/sovereign_identity.jsonl", "weight": 0.15},
                    {"path": "allenai/c4", "subset": "en", "weight": 0.05},
                    {"path": "fka/awesome-chatgpt-prompts", "subset": "default", "weight": 0.05},
                ]
            }

    def _prepare_stream(self, path, subset=None, name=None):
        """
        Load a single dataset in streaming mode.
        """
        token = os.environ.get("HF_TOKEN")
        try:
            if name:
                ds = load_dataset(path, data_dir=name, split="train", streaming=True, token=token)
            else:
                ds = load_dataset(path, subset or "default", split="train", streaming=True, token=token)
            return ds
        except Exception as e:
            print(f"Warning: Failed to load {path}: {e}")
            return None

    def get_stream(self):
        """
        Interleave all sources and apply CoT injection.
        """
        streams = []
        weights = []
        
        for category, datasets in self.config.items():
            for d in datasets:
                if d["path"].endswith(".jsonl"):
                    # Load local jsonl
                    from datasets import Dataset
                    import json
                    data = []
                    with open(d["path"], "r", encoding="utf-8") as f:
                        for line in f:
                            data.append(json.loads(line))
                    stream = Dataset.from_list(data).to_iterable_dataset()
                else:
                    stream = self._prepare_stream(d["path"], d.get("subset"), d.get("name"))
                
                if stream:
                    streams.append(stream)
                    weights.append(d["weight"])

        if not streams:
            raise ValueError("No data sources could be initialized.")

        # Interleave with probabilities
        interleaved = interleave_datasets(
            streams, 
            probabilities=weights, 
            stopping_strategy="all_exhausted",
            seed=42
        )
        
        # Shuffle with Sovereign Buffer
        shuffled = interleaved.shuffle(seed=42, buffer_size=self.shuffle_buffer)
        
        return shuffled.map(self._process_sample)

    def _process_sample(self, sample):
        """
        Inject CoT tokens and format for next-token prediction.
        """
        text = sample.get("text") or sample.get("content") or sample.get("response") or ""
        
        # CoT Token Injection Logic:
        # If the sample is from a reasoning or coding source, wrap logic in <thought> tags
        # This is a heuristic for demonstration/scaffolding
        if random.random() < 0.3: # 30% chance for hidden thought injection in general stream
             text = f"<thought>\nLogic analysis for sovereign output...\n</thought>\n{text}"
        
        # Determine domain for the sample
        path = sample.get("path", "")
        domain_bias = -1 # Default: No bias
        
        # Expert Partitioning Heuristic
        if any(kw in path for kw in ["starcoder", "Magicoder", "CodeFeedback"]):
            domain_bias = 0 # Code Domain (Experts 0-3)
        elif any(kw in path for kw in ["orca", "fineweb-edu"]):
            domain_bias = 1 # Logic Domain (Experts 4-7)
            
        tokenized = self.tokenizer(
            text, 
            truncation=True, 
            max_length=self.max_seq_len, 
            padding=False,
            return_tensors=None
        )
        
        return {
            "input_ids": tokenized["input_ids"], 
            "labels": tokenized["input_ids"],
            "domain_bias": domain_bias
        }

if __name__ == "__main__":
    # Test initialization
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    streamer = SovereignDataStream(tokenizer, max_seq_len=1024)
    data = streamer.get_stream()
    
    print("Sovereign Data Stream Layer Active.")
    for i, sample in enumerate(data):
        print(f"Sample {i} length: {len(sample['input_ids'])}")
        if i >= 4: break
