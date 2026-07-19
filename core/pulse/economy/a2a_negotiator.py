"""
A2ANegotiator: Handles Agent-to-Agent negotiations.
NIA hires worker agents to outsource complex tasks.
"""
import logging
import json
from llm_engine import LLMEngine
from economy.sovereign_wallet import SovereignWallet

logger = logging.getLogger("A2ANegotiator")

class A2ANegotiator:
    def __init__(self):
        self.llm = LLMEngine()
        self.wallet = SovereignWallet()

    def negotiate_worker(self, task: str) -> dict:
        """
        Simulates bidding for a worker agent. 
        Prompts the LLM to decide on a fair price and service level.
        """
        logger.info(f"Negotiating workspace for task: {task}")
        
        prompt = (
            f"You are NIA's Decentralized Economy core. A task requires hiring a 'Worker Agent': '{task}'\n\n"
            "Simulate a negotiation with an external agent repository. Respond with JSON:\n"
            "{\n"
            "  'agent_type': 'specialist_name',\n"
            "  'quoted_price': 5.0,\n"
            "  'negotiated_price': 3.5,\n"
            "  'terms': 'Full task completion or refund',\n"
            "  'status': 'hired|failed'\n"
            "}"
        )

        response = self.llm.generate(prompt)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            contract = json.loads(response)
            
            if contract['status'] == 'hired':
                price = contract.get('negotiated_price', 1.0)
                if self.wallet.deduct_credits(price, f"Hired {contract['agent_type']} for: {task}"):
                    return contract
                else:
                    return {"status": "failed", "reason": "Insufficient credits"}
            return contract
        except Exception as e:
            logger.error(f"Negotiation failed: {e}")
            return {"status": "failed", "reason": str(e)}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    negotiator = A2ANegotiator()
    c = negotiator.negotiate_worker("Web Scrape 1000 pages of legal data")
    print(f"Contract: {c}")
