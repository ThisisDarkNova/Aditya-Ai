import json
import os

class WealthManager:
    """
    💎 Vespera Wealth Manager: Personal Analytics
    Hooks into local email/PDF directories to track monthly subscriptions and spending securely.
    """
    def __init__(self, db_path="data/wealth_ledger.json"):
        self.db_path = db_path
        self.ledger = {"expenses": [], "subscriptions": []}
        self._load()

    def _load(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self.ledger = json.load(f)
            except Exception:
                pass

    def _save(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.ledger, f, indent=4)

    def log_expense(self, amount: float, vendor: str, category: str):
        self.ledger["expenses"].append({
            "amount": amount,
            "vendor": vendor,
            "category": category
        })
        self._save()
        print(f"[Wealth Manager] Logged expense: ${amount} at {vendor}.")

wealth_manager = WealthManager()
