import sys
import time
import socket
from typing import Optional
from requests.exceptions import ConnectionError
import requests
import random

from core.data_structures.blockchain import Block
from core.network import get_random_node
from node_client.config import Config

def get_nodes():
    """return the list of all the active nodes"""
    message = f"GET_NODES {Config.get_node_port()}"

    for _ in range(3):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((Config.dns_ip, Config.dns_port))

                s.sendall(message.encode('utf-8'))
                print(f"Sent: {message}")

                BUFF_SIZE = 4096
                data = b''
                while True:
                    part = s.recv(BUFF_SIZE)
                    data += part
                    if len(part) < BUFF_SIZE:
                        break
                print(f"Received: {data}")

                data_str = data.decode('utf-8')
                nodes = data_str.split(",")
                me = f"{Config.node_host}:{Config.get_node_port()}"
                if me in nodes:
                    nodes.remove(me)

                return nodes

        except socket.error as e:
            print(f"Couldn't get nodes from DNS (address: {Config.dns_ip}), retrying: {e}")
            time.sleep(0.2)

        raise ConnectionError(f"Server DNS is not reachable. {Config.dns_ip}:{Config.dns_port}")


def get_chain_last_block() -> Optional[dict]:
    """Ask a node for the last block on the chain"""
    if not get_nodes():
        return
    me = f"{Config.node_host}:{Config.get_node_port()}"
    for _ in range(3):
        target_node = get_random_node(exclude=[me])
        if target_node is None:
            return
        print(f"Asking {target_node} for last block in chain")
        try:
            r = requests.get(f"http://{target_node}/chain-last-block")
            if r.status_code == 200:
                print(f"Got last block from {target_node}")
                return r.json()
        except requests.exceptions.ConnectionError as e:
            print(f"Couldn't get chain last block from {target_node}, got exception: {e}")

    raise RuntimeError("Couldn't get last block in chain")


def send_block(dst_host: str,  block: Block) -> bool:
    """send block to the node destination"""
    url = f"http://{dst_host}/add-block"
    for i in range(3):
        try:
            response = requests.post(url, json=block.to_dict())
            if response.status_code == 200:
                return True
            else:
                print(f"Block {dst_host} doesn't like the block I tried to send him, got: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            pass

    print(f"Failed to connect to {dst_host}")
    return False


def broadcast_block(block: Block):
    """broadcast block to all the connected nodes"""
    print(f"Broadcasting block {block}")
    list_nodes = get_nodes()
    for node in list_nodes:
        success = send_block(node, block)
        print(f"Sent block to {node}, success={success}")
    return



def ping_dns_server():
    """ping the DNS server to stay as an active node"""
    message = f"PING {Config.get_node_port()}"
    for _ in range(5):
        try:
            # connect to the DNS server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((Config.dns_ip, Config.dns_port))

                # send message to DNS server
                s.sendall(message.encode('utf-8'))
                print(f"Sent: {message}")

                response = s.recv(1024).decode('utf-8')
                print(f"Received: {response}")

                if response == "OK":
                    return

        except socket.error as e:
            print(f"Connection error: {e}")
            time.sleep(0.5)

        raise RuntimeError(f"Server DNS is not reachable for pinging. {Config.dns_host}")



