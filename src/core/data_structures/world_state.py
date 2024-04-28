from __future__ import annotations

from core.data_structures.account import Account
from core.data_structures.smart_contract import SmartContract


class WorldState:
    def __init__(self, accounts: dict[str, Account], contracts: dict[str, SmartContract]):
        self.accounts = accounts
        self.contracts = contracts

    def get_account_balance(self, account_id) -> int:
        if account_id not in self.accounts:
            return 0

        return self.accounts[account_id].money_balance

    def __repr__(self):
        return f"<WorldState {self.accounts}, {self.contracts}>"

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def to_dict(self):
        return ({
            "accounts": {k: v.to_dict() for k,v in self.accounts.items()},
            "contracts": {k: v.to_dict() for k,v in self.contracts.items()}
        })

    @classmethod
    def from_dict(cls, data):
        return WorldState(
            accounts={k: Account.from_dict(v) for k,v in data["accounts"].items()},
            contracts={k: SmartContract.from_dict(v) for k,v in data["contracts"].items()}

            )

