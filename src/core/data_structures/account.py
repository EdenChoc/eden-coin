
from ecdsa import VerifyingKey
from core.security import Key, key_to_string, verifying_key_from_str


class Account:
    def __init__(self, public_key: VerifyingKey, money_balance: int, num_transfers: int, extra_storage: dict = None):
        self.public_key = public_key
        self.money_balance = money_balance
        self.num_transfers = num_transfers
        self.extra_storage = extra_storage or {}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            public_key = verifying_key_from_str(data["public_key"]),
            money_balance = data["money_balance"],
            num_transfers = data["num_transfers"],
            extra_storage = data["extra_storage"]
        )

    def to_dict(self):
        return {
             "public_key": key_to_string(self.public_key),
             "money_balance": self.money_balance,
             "num_transfers": self.num_transfers,
             "extra_storage": self.extra_storage,
        }


    def __repr__(self):
        return f"<Account {key_to_string(self.public_key)[:10]}>"

