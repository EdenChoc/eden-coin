import random
import uuid


class Config:

    dns_ip = "192.168.86.30"
    dns_port = 9494
    dns_host = "{dns_ip} {dns_port}"

    _node_port = None
    node_host = "127.0.0.1"
    node_id = str(uuid.uuid4())
    #node_id = "main" # TODO
    mainloop_sleep_sec = 10
    db_url = "mongodb://localhost:27017"
    db_name = "blockchain_nodes"

    @classmethod
    def get_blockchain_db_collection_name(cls):
        return f"blockchain-node-{cls.node_id}"

    @classmethod
    def get_node_port(cls):
        if cls._node_port is None:
            cls._node_port = random.choice(range(49152, 65333))  # TODO: handle port already taken

        return cls._node_port
