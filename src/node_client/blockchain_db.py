import base64
import threading
from typing import Optional
import pymongo

from node_client.config import Config
from core.security import Key, verifying_key_from_str
from core.data_structures.blockchain import Block

FIRST_BLOCK = {"index": 0, "timestamp": 1, "data": {"accounts": {"323bd920bf5462e1efc924703c3c65c8ee49c92033c0a6ba02ccfdf1cdb4964de83d2e0ba6a05bf69a8226a2ff57bf74": {"public_key": "323bd920bf5462e1efc924703c3c65c8ee49c92033c0a6ba02ccfdf1cdb4964de83d2e0ba6a05bf69a8226a2ff57bf74", "money_balance": 10000, "num_transfers": 89, "extra_storage": {}}}, "contracts": {"transfer_money": {"name": "transfer_money", "function_code": "\ndef _CONTRACT(world_state, executor_id, destination_id, amount):\n    amount = int(amount)\n    account_executor = world_state.accounts.get(executor_id)\n    account_destination = world_state.accounts.get(destination_id)\n    \n    if not account_executor:\n        raise ContractError(\"Executor account doesnt exist\")\n        \n    if account_executor.money_balance < amount:\n        raise ContractError(\"Not enough money in executor's account!\")\n\n    if not account_destination:\n        account_destination = Account(public_key=verifying_key_from_str(destination_id), money_balance=0, num_transfers=0)\n        world_state.accounts[destination_id] = account_destination\n        \n    account_executor.money_balance -= amount\n    account_destination.money_balance += amount\n\n    account_executor.num_transfers += 1\n\n    return world_state\n", "description": ""}, "add_contract": {"name": "add_contract", "function_code": "\ndef _CONTRACT(world_state, executor_id, name_contract, func_str, description=\"\"):\n    if name_contract in world_state.contracts:\n        raise ContractError(f\"The contract {name_contract} already exist!\")\n   \n    contract = SmartContract(name_contract, func_str, description)\n    world_state.contracts[name_contract] = contract\n\n    return world_state\n", "description": ""}}}, "previous_hash": "", "miner_id": "", "proof_of_work": 4191, "hash": "00025910e4b78d1c7fbcc625f07fd6872207e6eb"}

client = pymongo.MongoClient(Config.db_url)
collection = client[Config.db_name][Config.get_blockchain_db_collection_name()]
threadLock = threading.Lock()

def store_block(block: Block):
    """Store a block in the blockchain
    :param block: Block to store
    :return: True if the block has been inserted successfully, else an error string message
    """
    threadLock.acquire()
    """Store a block in the DB"""
    last_block = get_last_block()

    # Check POW
    if not block.is_pow_valid():
        print("the proof of work is invalid, try again")
        print(f"New block: {block}")
        return "Invalid POW"
    # Check if the last block in the chain: has the right index
    if block.index != last_block.index + 1:
        print("The index of the block is invalid")
        print(f"Last block: {last_block}")
        print(f"New block: {block}")
        return "Invalid last block index"
    # Check if the block has the right previous hash (block.previous_hash)
    if block.previous_hash != last_block.get_hash():
        print(f"The previous hash of the block is invalid")
        print(f"Last block: {last_block}")
        print(f"New block: {block}")
        return "Invalid previous hash"

    if block.transaction:
        # Check signature of payload
        signature_bytes = base64.b64decode(block.transaction["signature"].encode())
        executor_pubkey = verifying_key_from_str(block.transaction["payload"]["executor_pubkey"])
        if not Key.verify_dict(block.transaction["payload"], signature_bytes, executor_pubkey):
            print("Invalid signature")
            return "Invalid signature"

        # Check validity of transaction result
        contract = last_block.data.contracts[block.transaction["payload"]["id_program"]]
        result_world_state = contract.execute_contract(last_block.data, block.transaction["payload"]["executor_pubkey"], block.transaction["payload"]["params"])

        if block.data != result_world_state:
            print("World state output should not be this")
            return "World state output is incorrect"

    block_dict = block.to_dict()
    block_dict["_id"] = block_dict["index"]
    collection.insert_one(
        block_dict
    )
    print(f"Added block {block_dict['index']} to blockchain !")
    threadLock.release()

    return True

def get_blocks(indexes) -> list[Block]:
    """Return blocks with specified index"""
    r = collection.find({
        "index": {"$in": indexes}
    })
    # Create list of block objects from the dictionaries received
    blocks = []
    for block in r:
        blocks.append(Block.from_dict(block))

    return blocks


def get_last_block() -> Optional[Block]:
    """Return the last block in chain or None if the chain is empty"""
    r = collection.find().sort({"index":-1}).limit(1)
    try:
        block_dat = next(r)
    except StopIteration:
        return None
    return Block.from_dict(block_dat)


def insert_first_block(block_dict=None):
    """Insert the first block (not necessarily index 0) in the chain. DO NOT MODIFY THIS FUNCTION"""
    # For uniformization, convert to obj and back to dict
    if block_dict is None:
        print("First block is None, inserting hardcoded one")
        block_dict = FIRST_BLOCK

    block = Block.from_dict(block_dict)

    block_dict = block.to_dict()
    block_dict["_id"] = block_dict["index"]

    collection.insert_one(block_dict)

