import numpy as np
import torch
from typing import Dict, List, Optional

class LinguisticMapper:
    """
    NIA Linguistic Scaffolding (V13.7)
    Maps human language tokens to Hyperdimensional vectors (VSA).
    Uses the LLM as a teacher to seed semantic similarities.
    """
    def __init__(self, dimension: int = None):
        # Adaptive Dimensionality
        self.D = dimension if dimension else self._auto_detect_dimension()
        self.vocab: Dict[str, np.ndarray] = {}
        
        print(f"[MAPPER]: Linguistic Scaffolding active. Dimension: {self.D}")

    def _auto_detect_dimension(self) -> int:
        """Detects hardware power to set VSA density."""
        if torch.cuda.is_available():
            # Flagship/NPU detected
            return 10000
        else:
            # Low-power/Mobile
            return 2000

    def generate_random_hypervector(self) -> np.ndarray:
        """Returns a random D-dimensional bipolar vector {-1, 1}."""
        return np.random.choice([-1, 1], size=self.D).astype(np.int8)

    def seed_word(self, word: str, semantic_vector: Optional[np.ndarray] = None):
        """Anchors a word in the VSA space."""
        if semantic_vector is not None:
            self.vocab[word] = semantic_vector
        else:
            self.vocab[word] = self.generate_random_hypervector()

    def get_vector(self, word: str) -> np.ndarray:
        """Retrieves or creates a vector for a word."""
        if word not in self.vocab:
            self.seed_word(word)
        return self.vocab[word]

    def measure_similarity(self, word_a: str, word_b: str) -> float:
        """Measures cosine similarity between two linguistic anchors."""
        v1 = self.get_vector(word_a)
        v2 = self.get_vector(word_b)
        return np.dot(v1, v2) / self.D # Approximate since vectors are bipolar

    def export_semantic_map(self) -> Dict[str, List[int]]:
        """Exports the map for sovereign persistence (LLM-Independent)."""
        return {word: vec.tolist() for word, vec in self.vocab.items()}

if __name__ == "__main__":
    mapper = LinguisticMapper()
    mapper.seed_word("sovereign")
    mapper.seed_word("independent")
    sim = mapper.measure_similarity("sovereign", "independent")
    print(f"Similarity: {sim:.4f}")
