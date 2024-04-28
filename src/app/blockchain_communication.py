import base64
import random
import requests

from app.current_user import CurrentUser
from core.data_structures.world_state import WorldState
from core.network import get_random_node


def post_instruction(id_program: str, executor: str, params: dict, current_user: CurrentUser):
    payload = {
        "id_program": id_program,
        "executor_pubkey": executor,
        "params": params
    }
    signature_bytes = current_user.key.sign_dict(payload)
    signature_str = base64.b64encode(signature_bytes).decode()

    data = {
       "payload": payload,
       "signature": signature_str
    }

    node_host = get_random_node()
    url = f"http://{node_host}/post-instruction"
    response = requests.post(url, json=data)
    print(f"Sent instruction <{id_program}> to {node_host} with data: {data}, got: {response.text}")
    return response.status_code == 200


def get_world_state() -> WorldState:
    """Retrieve the current world state"""
    node_host = get_random_node()
    url = f"http://{node_host}/chain-last-block"
    response = requests.get(url)
    last_block = response.json()
    world_state = WorldState.from_dict(last_block["data"])
    return world_state


