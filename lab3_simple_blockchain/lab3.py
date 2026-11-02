"""Lab 3 - Simple blockchain with hash linkage, validation, tamper detection."""
import hashlib
import json
import time


class Block:
    def __init__(self, index, data, previous_hash, timestamp=None):
        self.index = index
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        payload = json.dumps({"index": self.index, "timestamp": self.timestamp,
                              "data": self.data, "previous_hash": self.previous_hash}, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = [Block(0, "Genesis Block", "0" * 64)]

    def add_block(self, data):
        prev = self.chain[-1]
        self.chain.append(Block(prev.index + 1, data, prev.hash))

    def validate(self, verbose=True):
        for i, b in enumerate(self.chain):
            if b.hash != b.compute_hash():
                if verbose:
                    print(f"  INVALID: block {b.index} content does not match its stored hash")
                return False
            if i > 0 and b.previous_hash != self.chain[i - 1].hash:
                if verbose:
                    print(f"  INVALID: block {b.index} previous_hash != hash of block {b.index - 1}")
                return False
        return True

    def show(self):
        for b in self.chain:
            print(f"  #{b.index} data={b.data!r}\n     prev={b.previous_hash[:20]}...\n     hash={b.hash[:20]}...")


if __name__ == "__main__":
    print("=== Tasks 1-2: create chain with 3 blocks (+genesis) ===")
    bc = Blockchain()
    for d in ["Alice pays Bob 10", "Bob pays Carol 4", "Carol pays Dave 2"]:
        bc.add_block(d)
    bc.show()

    print("\n=== Task 3: validate original chain ===")
    print("Chain valid:", bc.validate())

    print("\n=== Task 4a: tamper block 1 data (hash NOT recomputed) ===")
    bc.chain[1].data = "Alice pays Bob 1000"
    print("Chain valid:", bc.validate())

    print("\n=== Task 4b: attacker recomputes block 1 hash ===")
    bc.chain[1].hash = bc.chain[1].compute_hash()
    print("Chain valid:", bc.validate())

    print("\n=== Task 4c: attacker re-links ALL later blocks ===")
    for i in range(2, len(bc.chain)):
        bc.chain[i].previous_hash = bc.chain[i - 1].hash
        bc.chain[i].hash = bc.chain[i].compute_hash()
    print("Chain valid:", bc.validate(), "(only stopped by PoW / consensus - see Lab 4)")
    print("""
Explanation: each block stores the hash of its predecessor. Altering block 1
changes its hash, so block 2's previous_hash no longer matches, and the mismatch
cascades to every later block. To hide a change the attacker must recompute every
subsequent block; in a real network that also requires redoing proof-of-work
faster than honest nodes, which is computationally infeasible.""")
