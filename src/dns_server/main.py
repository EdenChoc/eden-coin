"""The DNS server is helping nodes to find the ip addresses of the other nodes
It should store a table of all the living nodes and update it when some join/leave
"""
import flask
import time
import pymongo


import socket
import threading


def start_server(server_ip, server_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, server_port))
    server.listen(10)
    print(f"Server listening on {server_ip}:{server_port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        # maybe need to add here something


def node_say_ping(client_socket):
    try:
        message = client_socket.recv(1024).decode('utf-8')
        print(f"Received: {message}")

        if message.startswith("PING"):
            _, port, last_pind_ts = message.split()
            ip = client_socket.getpeername()[0]

            collection.update_one(
                {"ip": ip, "port": port},
                {"$set": {
                    "last_ping_ts": float(last_pind_ts)}}
            )
            print(f"Node {ip}:{port} updated in the database.")

            response = "OK"
            client_socket.sendall(response.encode('utf-8'))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()


def node_say_bye(client_socket):
    try:
        message = client_socket.recv(1024).decode('utf-8')
        print(f"Received: {message}")

        if message.startswith("BYE"):
            _, port = message.split()
            ip = client_socket.getpeername()[0]

            collection.delete_one({
                "ip": ip,
                "port": port
            })
            print(f"Node {ip}:{port} removed from the database.")

            response = "OK"
            client_socket.sendall(response.encode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()


















                #old code:
PORT = 7070

DB_URL = "mongodb://localhost:27017"
DB_NAME = "blockchain_dns_server"
COLL_NAME = "nodes_info"
NODE_TTL_SEC = 35

app = flask.Flask("DNS_SERVER")

client = pymongo.MongoClient(DB_URL)
collection = client[DB_NAME][COLL_NAME]

@app.route("/ping/<port>")
def node_say_ping(port):
    collection.update_one(
        {"ip": flask.request.remote_addr , "port": port},
      {"$set": {
            "last_ping_ts": time.time()
        }},
        upsert=True
    )
    return "OK"


@app.route("/bye/<port>")
def node_say_bye(port):
    r = collection.delete_one({
        "ip": flask.request.remote_addr,
        "port": port
    })
    return "OK"


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
    app.run(port=PORT)

