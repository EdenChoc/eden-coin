"""The DNS server is helping nodes to find the ip addresses of the other nodes
It should store a table of all the living nodes and update it when some join/leave
"""
import threading
import time
import pymongo
import socket

from core.config import Config

DB_URL = "mongodb://localhost:27017"
DB_NAME = "blockchain_dns_server"
COLL_NAME = "nodes_info"
NODE_TTL_SEC = 35

client = pymongo.MongoClient(DB_URL)
collection = client[DB_NAME][COLL_NAME]

server_ip = Config.dns_ip
server_port = Config.dns_port

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, server_port))
    server.listen(10)
    print(f"Server listening on {server_ip}:{server_port}")

    while True:
        client_socket, addr = server.accept()
        host, port = client_socket.getpeername()

        print(f"Accepted connection from {host}")
        message = client_socket.recv(1024).decode('utf-8')
        print(f"Received: {message}")

        response = "ERROR"
        x = message.split()
        print(f"the lst is: {x}")
        port = x[1]
        if message.startswith("PING"):
            if node_say_ping(ip=host, port=port):
                response = "OK"

        if message.startswith("BYE"):
            if node_say_bye(ip=host, port=port):
                response = "OK"

        if message.startswith("GET_NODES"):
            response = get_nodes()

        if message.startswith("RESET"):
            if reset():
                response = "OK"

        client_socket.sendall(response.encode('utf-8'))
        client_socket.close()

def node_say_ping(ip, port):
    try:
        collection.update_one(
            {"ip": ip, "port": port},
            {"$set": {
                "last_ping_ts": int(time.time())
            }},
            upsert=True
        )
        print(f"Node {ip}:{port} updated in the database.")
        return True

    except Exception as e:
        print(f"Error: {e}")


def node_say_bye(ip, port):
    try:
        collection.delete_one({
            "ip": ip,
            "port": port
        })
        print(f"Node {ip}:{port} removed from the database.")
        return True

    except Exception as e:
        print(f"Error: {e}")



def get_nodes():
    try:
        nodes = collection.find({
        "last_ping_ts": {"$gt": time.time()-NODE_TTL_SEC}
        })
        nodes_list = [f"{n['ip']}:{n['port']}" for n in nodes]
        response = ",".join(nodes_list)
        return response
    except Exception as e:
        print(f"Error: {e}")
        return "Error"



def reset():
    collection.delete_many({})
    return True


if __name__ == '__main__':
    server_thread = threading.Thread(target=start_server())
    server_thread.start()




