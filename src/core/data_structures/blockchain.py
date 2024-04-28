import hashlib
import json
import time
from datetime import datetime
from typing import Optional

from core.data_structures.world_state import WorldState


class Block:
    def __init__(self, index: int, miner_id: str, data: WorldState, previous_hash: str, proof_of_work: int = 0, timestamp: float = None, transaction: Optional[dict] = None):
        self.index = index
        self.timestamp = timestamp or time.time()
        self.miner_id = miner_id
        self.data = data
        self.previous_hash = previous_hash
        self.proof_of_work = proof_of_work
        self.transaction = transaction

    def __repr__(self):
        dt = datetime.fromtimestamp(self.timestamp)
        return f"<Block no {self.index}, hash:{self.get_hash()}, prev-hash:{self.previous_hash}, pow:{self.proof_of_work} (mined by {self.miner_id} on {dt.isoformat()})>"

    def mine(self):
        """Try every proof of work number until the hash starts with three 0"""
        start = time.time()
        while not self.is_pow_valid():
            self.proof_of_work += 1

        print(f"Took {time.time()-start} secs to mine block, proof of work is {self.proof_of_work}")

    def is_pow_valid(self) -> bool:
        """Verify if the proof of work is valid - start with 000"""
        return self.get_hash().startswith("000")

    def to_dict(self, with_hash=True):
        d = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data.to_dict(),
            "previous_hash": self.previous_hash,
            "miner_id": self.miner_id,
            "proof_of_work": self.proof_of_work,
            "transaction": self.transaction
        }
        if with_hash:
            d["hash"] = self.get_hash()
        return d

    @classmethod
    def from_dict(cls, block_dat: dict):
        return cls(
            index=block_dat["index"],
            timestamp=block_dat.get("timestamp"),
            data=WorldState.from_dict(block_dat["data"]),
            previous_hash=block_dat["previous_hash"],
            miner_id=block_dat["miner_id"],
            proof_of_work=block_dat.get("proof_of_work", 0),
            transaction=block_dat.get("transaction")
        )

    def get_hash(self) -> str:
        obj_string = json.dumps(self.to_dict(with_hash=False), sort_keys=True)
        # To make it more secure, use harder hash function like hashlib.sha256
        return hashlib.sha1(obj_string.encode()).hexdigest()

if __name__ == '__main__':
    pass
