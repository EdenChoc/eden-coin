import base64

import flask

from node_client.blockchain_db import store_block, get_last_block
from node_client.config import Config
from core.security import Key, verifying_key_from_str
from core.data_structures.blockchain import Block
from node_client.network import broadcast_block

# Create server

app = flask.Flask("NODE")


# ROUTES:

# GUI -> NODE
@app.route("/post-instruction", methods=["POST"])
def post_instruction():
    """
    POST body should be a json containing:
    signature: The signature of the payload
    payload: A dict containing:
        id_program: the id of the program to execute
        executor_pubkey: The public key of the account executing this instruction
        params: a dictionary of key-value parameters
    """
    # Verify signature
    args = flask.request.json
    signature = args["signature"]
    payload = args["payload"]

    print(f"Received instruction from {flask.request.remote_addr}:{flask.request.environ['REMOTE_PORT']}, payload={payload}")

    signature_bytes = base64.b64decode(signature.encode())
    executor_pubkey = verifying_key_from_str(payload["executor_pubkey"])
    if not Key.verify_dict(payload, signature_bytes, executor_pubkey):
        print("Signature is invalid")
        return "Signature is invalid", 400
   
    last_block = get_last_block()
    world_state = last_block.data

    # Execute contract to get new world state
    contract = world_state.contracts[payload["id_program"]]
    new_world_state = contract.execute_contract(world_state, payload["executor_pubkey"], payload["params"])

    # Create new block
    last_block = get_last_block()
    new_index = last_block.index + 1

    print(f"Executed contract {payload['id_program']}, creating block {new_index}")
    block = Block(
        index= new_index,
        miner_id=Config.node_id,
        data=new_world_state,
        previous_hash=last_block.get_hash(),
        transaction=args
    )

    # Mine it
    block.mine()

    # Store it
    store_block(block)

    # Broadcast it
    broadcast_block(block)

    print(f"Block {block} successfully mined and broadcast")

    return "OK", 200



# NODE -> NODE
@app.route("/add-block", methods=["POST"])
def add_block():
    """add block to the chain"""
    block_dict = flask.request.json

    block = Block.from_dict(block_dict)

    print(f"Received block {block.index} from {flask.request.remote_addr}:{flask.request.environ['REMOTE_PORT']}")

    if not block.transaction:
        print(f"Transaction for block {block.index} is missing")
        return f"Transaction for block {block.index} is missing", 400


    # Add block to chain
    try:
        result = store_block(block)
    except Exception as e:
        return f"Exception: {e}"

    if result is True:
        print(f"Block {block.index} added to the chain")
        return "OK", 200
    else:
        return result, 400

@app.route("/chain-last-block")
def get_chain_last_block():
    last_block_dict = get_last_block().to_dict()
    return last_block_dict


@app.route("/hey")
def hey():
    """Just check that you're alive"""
    return "hey"

