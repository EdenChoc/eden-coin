"""The DNS server is helping nodes to find the ip addresses of the other nodes
It should store a table of all the living nodes and update it when some join/leave
"""
import flask
import time
import pymongo

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

