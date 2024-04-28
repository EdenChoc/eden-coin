import random

from core.security import key_to_string, Key
from core.data_structures.blockchain import Block
from core.data_structures.smart_contract import SmartContract
from core.data_structures.world_state import WorldState
from core.data_structures.world_state import Account

def gen_fake_account(money_balance=None):
        money_balance = money_balance or random.randint(1,5000)
        key = Key()
        pubkey = key.public_key
        acc = Account(public_key=pubkey, money_balance=money_balance, num_transfers=random.randint(1,100))

        print("Created fake account:")
        print(f"Money: {acc.money_balance}")
        print(f"Public key: {key_to_string(acc.public_key)}")
        print(f"Seed phrase: {key.get_seed_phrase()}")
        print("="*50)

        return acc


# self.index = index
#         self.timestamp = timestamp or time.time()
#         self.miner_id = miner_id
#         self.data = data
#         self.previous_hash = previous_hash
#         self.proof_of_work = proof_of_work
#
# W
transfer_money_func = """
def _CONTRACT(world_state, executor_id, destination_id, amount):
    amount = int(amount)
    account_executor = world_state.accounts.get(executor_id)
    account_destination = world_state.accounts.get(destination_id)
    
    if not account_executor:
        raise ContractError("Executor account doesnt exist")
        
    if account_executor.money_balance < amount:
        raise ContractError("Not enough money in executor's account!")

    if not account_destination:
        account_destination = Account(public_key=verifying_key_from_str(destination_id), money_balance=0, num_transfers=0)
        world_state.accounts[destination_id] = account_destination
        
    account_executor.money_balance -= amount
    account_destination.money_balance += amount

    account_executor.num_transfers += 1

    return world_state
"""

add_contract_func = """
def _CONTRACT(world_state, executor_id, name_contract, func_str, description=""):
    if name_contract in world_state.contracts:
        raise ContractError(f"The contract {name_contract} already exist!")
   
    contract = SmartContract(name_contract, func_str, description)
    world_state.contracts[name_contract] = contract

    return world_state
"""

transfer_money= SmartContract("transfer_money", transfer_money_func)
print(transfer_money.get_contract_params())
add_contract = SmartContract("add_contract", add_contract_func)
accounts = {}
acc = gen_fake_account(money_balance=10000)
id = key_to_string(acc.public_key)
accounts[id] = acc

world_state = WorldState(
        accounts=accounts,
        contracts={
                "transfer_money":transfer_money,
                "add_contract": add_contract
        }
)
first_block = Block(index=0, timestamp=1, miner_id="", data= world_state, previous_hash="")
first_block.mine()
pass

import json
print(json.dumps(first_block.to_dict()))