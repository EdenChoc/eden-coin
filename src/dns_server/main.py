"""The DNS server is helping nodes to find the ip addresses of the other nodes
It should store a table of all the living nodes and update it when some join/leave
"""
import threading

import flask
import time
import pymongo


import socket

from core.config import Config

PORT = 7474

DB_URL = "mongodb://localhost:27017"
DB_NAME = "blockchain_dns_server"
COLL_NAME = "nodes_info"
NODE_TTL_SEC = 35

app = flask.Flask("DNS_SERVER")

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
        print(f"Accepted connection from {addr}")
        message = client_socket.recv(1024).decode('utf-8')
        print(f"Received: {message}")

        response = "NO"
        msg_lst = message.split()
        port = msg_lst[1]
        if message.startswith("PING"):
            if node_say_ping(ip=addr, port=port):
                response = "OK"

        if message.startswith("BYE"):
            if node_say_bye(ip=addr, port=port):
                response = "OK"

        client_socket.sendall(response.encode('utf-8'))

        client_socket.close()

def node_say_ping(ip, port):
    try:
        collection.update_one(
            {"ip": ip, "port": port},
            {"$set": {
                "last_ping_ts": int(time.time())}}
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


@app.route("/get-nodes")
def get_nodes():
    nodes = collection.find({
        "last_ping_ts": {"$gt": time.time()-NODE_TTL_SEC}
    })
    nodes = [f"{n['ip']}:{n['port']}" for n in nodes]
    return flask.jsonify(nodes)


@app.route("/reset")
def reset():
    collection.delete_many({})
    return "OK"


if __name__ == '__main__':
    server_thread = threading.Thread(target=start_server())
    server_thread.start()

    app.run(port=server_port)


