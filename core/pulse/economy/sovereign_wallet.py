"""
SovereignWallet: NIA's local credit management system.
Handles micro-payments and A2A transaction accounting.
"""
import logging
import json
import os

logger = logging.getLogger("SovereignWallet")

class SovereignWallet:
    def __init__(self):
        self.wallet_path = os.path.join(os.path.dirname(__file__), "wallet.json")
        self.balance = 0.0
        self.transactions = []
        self._load_wallet()

    def _load_wallet(self):
        """Loads balance and history from local storage."""
        if os.path.exists(self.wallet_path):
            with open(self.wallet_path, "r") as f:
                data = json.load(f)
                self.balance = data.get("balance", 100.0) # Start with 100 credits
                self.transactions = data.get("transactions", [])
        else:
            self.balance = 100.0
            self.transactions = []
            self._save_wallet()
        logger.info(f"Wallet loaded. Current Balance: {self.balance} NIA Credits")

    def _save_wallet(self):
        with open(self.wallet_path, "w") as f:
            json.dump({"balance": self.balance, "transactions": self.transactions}, f, indent=2)

    def deduct_credits(self, amount: float, reason: str):
        if self.balance >= amount:
            self.balance -= amount
            self.transactions.append({"type": "debit", "amount": amount, "reason": reason})
            self._save_wallet()
            logger.info(f"Deducted {amount} credits for: {reason}. New Balance: {self.balance}")
            return True
        logger.warning(f"Insufficient funds for: {reason}")
        return False

    def add_credits(self, amount: float, reason: str):
        self.balance += amount
        self.transactions.append({"type": "credit", "amount": amount, "reason": reason})
        self._save_wallet()
        logger.info(f"Added {amount} credits for: {reason}. New Balance: {self.balance}")

    def get_history(self):
        return self.transactions

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    wallet = SovereignWallet()
    wallet.deduct_credits(5.0, "API Token Usage")
