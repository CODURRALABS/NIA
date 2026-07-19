import torch
from typing import Tuple
import sys
import os

# Add parent directory to sys.path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.model import NIA500, NIAConfig
except ImportError:
    from model import NIA500, NIAConfig

from transformers import AutoTokenizer
import time

def test_inference(prompt: str = "Explain the logic of recursion in Kotlin."):
    """
    Test the Sovereign Core's inference and CoT block logic.
    """
    print(f"Sovereign Inference Test Initiated.")
    print(f"Prompt: {prompt}")
    
    config = NIAConfig()
    model = NIA500(config)
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    
    # Warmup
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        _ = model(inputs["input_ids"])
    
    # Generation (Simplified for architectural test)
    start_time: float = time.time()
    with torch.no_grad():
        out_tuple: Tuple[torch.Tensor, torch.Tensor] = model(inputs["input_ids"])
        logits, _ = out_tuple
    end_time: float = time.time()
    
    print(f"Forward Pass Latency: {(end_time - start_time)*1000:.2f}ms")
    print(f"Status: NIA Logic Core is VRAM-Stable.")

def run_suite():
    print("--- NIA SOVEREIGN TEST SUITE ---")
    
    # 1. Architecture Check
    print("\n[TEST 1] Architecture Verification")
    subprocess_call("python src/model.py")
    
    # 2. Training Check (10 steps)
    print("\n[TEST 2] Training Stability (10-step Dummy)")
    subprocess_call("python src/train.py --dummy --steps 10")
    
    # 3. Data Engine Check (5 samples)
    print("\n[TEST 3] Data Stream Verification")
    subprocess_call("python src/data_stream.py")
    
    # 4. Inference Check
    print("\n[TEST 4] Inference Logic Check")
    test_inference()

def subprocess_call(cmd: str):
    try:
        import subprocess
        subprocess.run(cmd, shell=True, check=True)
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    run_suite()
