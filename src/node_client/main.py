import time
import threading

from node_client.blockchain_db import get_last_block, insert_first_block
from node_client.config import Config
from node_client.network import ping_dns_server, get_chain_last_block
from node_client.server import app

print(f"Started node with id {Config.node_id} (port: {Config.get_node_port()})")

def mainloop():
    curr_last_block = get_chain_last_block()
    insert_first_block(curr_last_block)
    print("Current last block:", get_last_block())

    while True:
        ping_dns_server()
        time.sleep(Config.mainloop_sleep_sec)


ping_dns_server()

# Thread 1: Loop
mainloop_thread = threading.Thread(target=mainloop)
mainloop_thread.start()

# Main thread: app
app.run(host="0.0.0.0", port=Config.get_node_port())