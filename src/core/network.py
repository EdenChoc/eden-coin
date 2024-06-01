import time
import socket
import requests
import random

from core.config import Config


def get_random_node(exclude: list[str] = None):
    """Retrieve a random node host"""
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

        except socket.error as e:
            print(f"Couldn't connect to server DNS (address: {Config.dns_ip}), retrying: {e}")
            time.sleep(0.2)

        raise ConnectionError(f"Server DNS is not reachable. {Config.dns_ip}:{Config.dns_port}")