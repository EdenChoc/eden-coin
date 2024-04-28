import requests
import random

from core.config import Config

def get_random_node(exclude: list[str] = None):
    """Retrieve a random node host"""
    url = f"{Config.dns_host}/get-nodes"
    response = requests.get(url)
    nodes = response.json()

    random.shuffle(nodes)
    for node_host in nodes:
        if exclude and node_host in exclude:
            continue
        url = f"http://{node_host}/hey"
        try:
            requests.get(url, timeout=3)
        except requests.exceptions.ConnectionError:
            continue
        return node_host

    print("No nodes reachable.")
    return None