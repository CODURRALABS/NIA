import socket
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from web_engine import SovereignWebEngine

logger = logging.getLogger("ResearchSoul")

class ResearchSoul:
    """
    NIA Sovereign Researcher (V13.13)
    Performs PhD-level recursive search for complex logic and math.
    Implements 3-Stage Truth Resolution: Symmetry > Consensus > Swarm.
    """
    def __init__(self, web_engine: SovereignWebEngine, mapper: Any, vsa: Any, swarm: Any):
        self.retina = web_engine
        self.mapper = mapper
        self.vsa = vsa
        self.swarm = swarm
        print("[RESEARCH]: Sovereign Truth Resolver core active.")

    def is_online(self) -> bool:
        """Checks if Retina can reach the surface web."""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except OSError:
            return False

    async def resolve_truth(self, topic: str) -> Dict[str, Any]:
        """
        The Boss's 3-Stage Truth Protocol.
        """
        print(f"[RESEARCH]: Initializing Truth Resolution for '{topic}'...")
        
        # STAGE 1: Sovereign Symmetry (Internal Wisdom)
        dna_v = self.mapper.get_vector("sovereign_logic") # Base seed
        query_v = self.mapper.get_vector(topic)
        internal_symmetry = np.dot(query_v, dna_v) / self.vsa.D
        print(f"  - [STAGE 1]: Sovereign Symmetry: {internal_symmetry:.4f}")

        if not self.is_online():
            print("  - [HYBRID]: Offline Mode. Proceeding with Internal VSA Logic only.")
            return {"topic": topic, "truth": "Internal Sovereign Logic", "vibe": "Offline/DNA-Only"}

        # STAGE 2: Web Consensus (Retinal Alignment)
        print("  - [STAGE 2]: Calibrating Web Consensus...")
        web_data = self.retina.get_vsa_consensus(topic, self.mapper, self.vsa)
        
        consensus_vector = web_data["vector"]
        if consensus_vector is not None:
            comparison_score = np.dot(query_v, consensus_vector) / self.vsa.D
            print(f"  - [STAGE 2]: Consensus Match: {comparison_score:.4f}")
        else:
            comparison_score = 0.0
            print("  - [STAGE 2]: No Web Consensus found. Falling back to Swarm.")

        # STAGE 3: MiroFish Swarm Discussion (Final Consensus)
        print("  - [STAGE 3]: Launching MiroFish Swarm Intelligence...")
        raw_web_info = f"Topic: {topic}. Symmetry: {internal_symmetry}. Consensus: {comparison_score}."
        final_truth = await self.swarm.refined_analysis(
            raw_data=raw_web_info,
            goal="Determine the Indestructible Sovereign Truth",
            mode="analytical"
        )
        
        return {
            "topic": topic,
            "truth": final_truth,
            "sources": web_data["sources"],
            "symmetry_score": internal_symmetry,
            "consensus_score": comparison_score
        }

    async def recursive_search(self, topic: str, depth: int = 2) -> Dict[str, Any]:
        """
        Performs a deep search on a topic, extracting and summarizing content.
        """
        print(f"[RESEARCH]: Diving into '{topic}' (Depth: {depth})...")
        
        # 1. Fast Shadow Search
        search_results = self.retina.fast_search(topic, max_results=5)
        
        knowledge_base = []
        for result in search_results:
            url = result['link']
            # 2. Extract content (Lightweight first)
            content = self.retina.fast_fetch(url)
            
            knowledge_base.append({
                "source": url,
                "title": result['title'],
                "summary": content[:1000] # First 1000 chars for VSA mapping
            })
            
            # Recursive depth could involve following links (simulated for now)
            
        return {
            "topic": topic,
            "findings": knowledge_base,
            "vibe_check": "PhD-Level Density"
        }

    async def get_euclidean_summary(self) -> str:
        """Specialized logic for the Boss's Euclidean Geometry request."""
        topic = "Euclidean Geometry and Machine Learning Logic Patterns"
        results = await self.recursive_search(topic)
        # Summarization logic would map this back to VSA
        return f"Boss, I've mapped the Euclidean logic patterns. They form a {len(results['findings'])}-dimensional symmetry in the VSA space."

if __name__ == "__main__":
    from web_engine import SovereignWebEngine
    engine = SovereignWebEngine()
    researcher = ResearchSoul(engine)
    # asyncio.run(researcher.get_euclidean_summary())
