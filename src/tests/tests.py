
contract_func = """
def _CONTRACT(world_state, executor_id):
    return world_state
"""
import json
print(json.dumps({"f": contract_func}))


simplest_contract = """
def _CONTRACT()
    print("hello world")
"""











