
from typing import Protocol, TYPE_CHECKING
import inspect
# noinspection PyUnresolvedReferences
from core.data_structures.account import Account
# noinspection PyUnresolvedReferences
from core.security import verifying_key_from_str


if TYPE_CHECKING:
    from core.data_structures.world_state import WorldState

class SmartContractFunction(Protocol):
    def __call__(self, world_state: "WorldState", executor_id: str, **kwargs) -> "WorldState": ...


class ContractError(Exception):
    pass


class SmartContract:
    def __init__(self, name: str, function_code: str, description: str = ""):
        self.name = name
        self.function_code = function_code
        self.description = description

    def get_contract_params(self):
        try:
            exec(self.function_code, globals())
            params = inspect.getargspec(_CONTRACT).args
            return params[2:]
        except Exception as e:
            raise ContractError("Cannot execute contract, probably invalid:", e)

    def execute_contract(self, world_state: "WorldState", executor_id: str, params: dict) -> "WorldState":
        """We suppose the contract is finite and will not execute infinitely. This function should execute
        the contract as a thread with a timeout.
        """
        try:
            exec(self.function_code, globals())
            new_world_state = _CONTRACT(world_state,executor_id,**params)
            return new_world_state
        except Exception as e:
            raise ContractError("Cannot execute contract, probably invalid:",e)


    def to_dict(self):
        return {
            "name": self.name,
            "function_code": self.function_code,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name= data["name"],
            function_code=data["function_code"],
            description= data["description"]

        )


    def __repr__(self):
        return f"<SmartContract {self.name}>"

