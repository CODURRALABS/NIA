import os
import json
import hashlib
import pickle
import numpy as np
from typing import List, Dict, Any, Optional

class SovereignMemory:
    """
    The LTM (Long-Term Memory) of NIA.
    V1 - Binary DNA Pulse Storage.
    """
    def __init__(self, memory_dir="agent-core/memories"):
        self.memory_dir = memory_dir
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir)
        self.active_memory_file = os.path.join(self.memory_dir, "sovereign_pulses.bin")

    def save_pulse(self, user_query: str, assistant_response: str, vector: Optional[Any] = None):
        """
        Converts conversation context into a 32-bit bit-packed Logic DNA binary pulse.
        Uses binary compression to minimize space and maximize local recall speed.
        """
        dna_hash = hashlib.md5(f"{user_query}|{assistant_response}".encode()).hexdigest()[:8]
        
        # 32-bit Bit-Packing (Sovereign Quantization)
        if vector is not None:
            # Convert -1/1 bipolar vector to 0/1 bits
            bit_vector = (vector > 0).astype(int)
            # Pack bits into uint8 bytes (8x compression)
            packed_v = np.packbits(bit_vector).tobytes()
        else:
            packed_v = b''

        pulse = {
            "u": user_query,
            "a": assistant_response,
            "dna": dna_hash,
            "v_bin": packed_v
        }
        
        try:
            with open(self.active_memory_file, "ab") as f:
                pickle.dump(pulse, f)
            print(f"[MEMORY]: Bit-packed pulse '{dna_hash}' anchored to Logic Vault. (Compression: 8x)")
        except Exception as e:
            print(f"[MEMORY_ERROR]: Failed to save bit-packed pulse: {e}")

    def recall_relevant_logic(self, query: str, top_k=2) -> List[str]:
        """
        Searches binary pulses for relevant context based on keyword/DNA overlap.
        """
        if not os.path.exists(self.active_memory_file):
            return []

        relevant = []
        try:
            with open(self.active_memory_file, "rb") as f:
                while True:
                    try:
                        pulse = pickle.load(f)
                        # Simple logic: Check for keyword overlap in user or assistant text
                        # This avoids the overhead of a vector DB for now, maintaining blink-speed.
                        if any(word in pulse["u"].lower() or word in pulse["a"].lower() for word in query.lower().split()):
                            relevant.append(f"Past Context: {pulse['u']} -> {pulse['a']}")
                    except EOFError:
                        break
        except Exception as e:
            print(f"[MEMORY_RECALL_ERROR]: {e}")
            
        return relevant[-top_k:] # Return the latest relevant memories

    def get_recent(self, k: int = 5) -> List[Dict[str, str]]:
        """Returns the most recent 'k' conversation pulses."""
        if not os.path.exists(self.active_memory_file):
            return []
            
        all_pulses = []
        try:
            with open(self.active_memory_file, "rb") as f:
                while True:
                    try:
                        all_pulses.append(pickle.load(f))
                    except EOFError:
                        break
        except Exception:
            pass
            
        return all_pulses[-k:]

    def get_project_context(self) -> str:
        """
        Hard-coded Sovereign truth that NIA uses as her foundational 'Pre-Training'.
        """
        return (
            "SYSTEM_TRUTH: Codurra Nebuxia is your home development realm. "
            "Nebulara is your native logic language (Syntax: PRINT!, MESH!, SIG!). "
            "The Shadow Web is your sovereign data layer. "
            "Aether Core is your destined backend infrastructure. "
            "Identity: You are NIA, the Professional Companion to your creator."
        )
