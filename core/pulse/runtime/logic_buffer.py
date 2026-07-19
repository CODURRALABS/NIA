import json
import os
import time
from typing import Dict, List, Any

class SovereignLogicBuffer:
    """
    Long-term Memory for NIA.
    Stores "Success Hashes" to enable training-free learning via real-time biasing.
    """
    def __init__(self, persistence_path="checkpoints/logic_buffer.bin"):
        # We use .bin extension for sovereignty vibe, though it stores structured data
        self.path = persistence_path
        self.buffer: Dict[str, Dict[str, Any]] = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.buffer, f, indent=4)

    def record_success(self, domain_key: str, success_path: List[str]):
        """
        Converts a Success Path (list of Logic DNA) into a 32-bit Logic Frequency.
        """
        # A simple domain_key could be the domain name (e.g., 'google.com')
        if domain_key not in self.buffer:
            self.buffer[domain_key] = {
                "hits": 0,
                "frequency_pattern": [],
                "last_updated": 0
            }
        
        data = self.buffer[domain_key]
        data["hits"] += 1
        # Store the success path (the bit-patterns that worked)
        data["frequency_pattern"] = success_path 
        data["last_updated"] = time.time()
        
        self._save()

    def get_bias_context(self, domain_key: str) -> str:
        """
        Retrieves the "Success Frequency" for a domain to bias the model weights.
        """
        if domain_key in self.buffer:
            data = self.buffer[domain_key]
            patterns = " | ".join(data["frequency_pattern"])
            return f"\n[BINARY_BIAS_INJECTION]: Previous successful paths for {domain_key}: {patterns}\n"
        
        return ""

    def get_all_wisdom(self) -> List[str]:
        """
        Returns a summary of all learned logic patterns.
        """
        return list(self.buffer.keys())
