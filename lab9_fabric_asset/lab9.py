"""Lab 9 - Hyperledger Fabric asset transaction flow (SIMULATION in pure Python).

This models Fabric's execute-order-validate architecture; it is NOT a real Fabric
network (no Docker/fabric binaries are used). Concepts modelled:
  channel with 2 orgs (Org1, Org2), 1 peer each, a solo orderer, an asset-transfer
  chaincode, endorsement policy AND(Org1.peer, Org2.peer), signed endorsements,
  read/write sets with versions (MVCC), blocks with hash chain, world state per peer.
"""
import hashlib
import json
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature


def H(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True).encode()).hexdigest()


class Identity:
    def __init__(self, name):
        self.name = name
        self.key = ec.generate_private_key(ec.SECP256R1())  # Fabric uses P-256 ECDSA
        self.pub = self.key.public_key()

    def sign(self, payload):
        return self.key.sign(json.dumps(payload, sort_keys=True).encode(), ec.ECDSA(hashes.SHA256()))


def verify(pub, payload, sig):
    try:
        pub.verify(sig, json.dumps(payload, sort_keys=True).encode(), ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False


class Chaincode:
    """asset-transfer: CreateAsset / ReadAsset / TransferAsset / UpdateAsset. Runs against a state snapshot."""

    @staticmethod
    def invoke(state, fn, args):
        reads, writes = {}, {}

        def get(k):
            reads[k] = state.get(k, {}).get("version", 0)
            return state.get(k, {}).get("value")

        if fn == "CreateAsset":
            id_, color, size, owner = args
            if get(id_) is not None:
                raise ValueError(f"asset {id_} already exists")
            writes[id_] = {"ID": id_, "color": color, "size": int(size), "owner": owner}
        elif fn == "TransferAsset":
            id_, new_owner = args
            a = get(id_)
            if a is None:
                raise ValueError(f"asset {id_} does not exist")
            writes[id_] = dict(a, owner=new_owner)
        elif fn == "UpdateAsset":
            id_, color, size = args
            a = get(id_)
            if a is None:
                raise ValueError(f"asset {id_} does not exist")
            writes[id_] = dict(a, color=color, size=int(size))
        elif fn == "ReadAsset":
            return get(args[0]), {}, reads
        else:
            raise ValueError("unknown function " + fn)
        return None, writes, reads


class Peer:
    def __init__(self, name, org):
        self.name, self.org = name, org
        self.id = Identity(name)
        self.state = {}      # world state: key -> {value, version}
        self.ledger = []     # blocks

    def endorse(self, proposal):
        """EXECUTE phase: simulate chaincode on the current state, sign the result. State is NOT changed."""
        _, writes, reads = Chaincode.invoke(self.state, proposal["fn"], proposal["args"])
        rwset = {"reads": reads, "writes": writes}
        resp = {"proposal": H(proposal), "rwset": rwset}
        return {"peer": self.name, "org": self.org, "response": resp, "sig": self.id.sign(resp), "pub": self.id.pub}

    def query(self, key):
        return self.state.get(key, {}).get("value")

    def validate_and_commit(self, block, policy_orgs):
        """VALIDATE + COMMIT phase."""
        results = []
        for tx in block["txs"]:
            code = "VALID"
            orgs = set()
            for e in tx["endorsements"]:
                if not verify(e["pub"], e["response"], e["sig"]):
                    code = "BAD_ENDORSEMENT_SIGNATURE"
                    break
                if e["response"]["rwset"] != tx["rwset"]:
                    code = "ENDORSEMENT_MISMATCH"
                    break
                orgs.add(e["org"])
            if code == "VALID" and not policy_orgs.issubset(orgs):
                code = "ENDORSEMENT_POLICY_FAILURE"
            if code == "VALID":  # MVCC: versions read at simulation must still be current
                for k, v in tx["rwset"]["reads"].items():
                    if self.state.get(k, {}).get("version", 0) != v:
                        code = "MVCC_READ_CONFLICT"
                        break
            if code == "VALID":
                for k, v in tx["rwset"]["writes"].items():
                    self.state[k] = {"value": v, "version": self.state.get(k, {}).get("version", 0) + 1}
            results.append((tx["txid"], code))
        self.ledger.append({**{k: block[k] for k in ("number", "prev_hash", "data_hash")}, "flags": [c for _, c in results]})
        return results


class Orderer:
    """Solo orderer: orders txs, cuts blocks, does NOT execute chaincode."""

    def __init__(self):
        self.pending, self.height, self.prev = [], 0, "0" * 64

    def broadcast(self, tx):
        self.pending.append(tx)

    def cut_block(self):
        txs, self.pending = self.pending, []
        data = [{"txid": t["txid"], "rwset": t["rwset"]} for t in txs]
        block = {"number": self.height, "prev_hash": self.prev, "data_hash": H(data), "txs": txs}
        self.prev, self.height = H({k: block[k] for k in ("number", "prev_hash", "data_hash")}), self.height + 1
        return block


class Channel:
    def __init__(self):
        self.peers = [Peer("peer0.org1", "Org1"), Peer("peer0.org2", "Org2")]
        self.orderer = Orderer()
        self.policy = {"Org1", "Org2"}   # AND('Org1.peer','Org2.peer')
        self.counter = 0

    def submit(self, fn, *args, endorsers=None, quiet=False):
        self.counter += 1
        txid = f"tx{self.counter:03d}"
        proposal = {"txid": txid, "fn": fn, "args": list(args)}
        say = (lambda *a: None) if quiet else print
        say(f"  1. PROPOSAL     client -> {[p.name for p in (endorsers or self.peers)]}: {fn}{args}")
        ends = [p.endorse(proposal) for p in (endorsers or self.peers)]
        say(f"  2. ENDORSEMENT  {len(ends)} signed responses; rwset = {json.dumps(ends[0]['response']['rwset'])}")
        tx = {"txid": txid, "endorsements": ends, "rwset": ends[0]["response"]["rwset"]}
        self.orderer.broadcast(tx)
        return tx

    def order_and_commit(self, quiet=False):
        block = self.orderer.cut_block()
        say = (lambda *a: None) if quiet else print
        say(f"  3. ORDERING     orderer cut block #{block['number']} with {len(block['txs'])} tx (no chaincode executed)")
        for p in self.peers:
            res = p.validate_and_commit(block, self.policy)
            say(f"  4. VALIDATION   {p.name}: {res}")
        say(f"  5. COMMIT       block #{block['number']} appended on all peers; world state updated for VALID txs")
        return res


def show_state(ch):
    for p in ch.peers:
        print(f"    {p.name} state: {json.dumps({k: v['value'] | {'v': v['version']} for k, v in p.state.items()}, sort_keys=True)}")


if __name__ == "__main__":
    ch = Channel()
    print("=== Task 1: channel 'mychannel' ===")
    for p in ch.peers:
        print(f"  peer {p.name} (org {p.org}) joined; chaincode 'basic' installed; policy = AND(Org1, Org2)")

    print("\n=== Task 2: create + query asset ===")
    ch.submit("CreateAsset", "asset1", "blue", "5", "Tomoko")
    ch.order_and_commit()
    print("  Query asset1 on peer0.org2:", ch.peers[1].query("asset1"))

    print("\n=== Task 3: transfer asset1 to Brad, verify ledger/world state ===")
    ch.submit("TransferAsset", "asset1", "Brad")
    ch.order_and_commit()
    show_state(ch)
    assert all(p.query("asset1")["owner"] == "Brad" for p in ch.peers)
    print("  both peers agree: owner = Brad (version incremented to 2)")
    print("  ledger height:", [len(p.ledger) for p in ch.peers], "| block flags:", [b["flags"] for b in ch.peers[0].ledger])

    print("\n=== Task 4a: troubleshoot - tx endorsed by ONLY Org1 (policy needs both) ===")
    ch.submit("UpdateAsset", "asset1", "red", "9", endorsers=[ch.peers[0]])
    ch.order_and_commit()
    print("  asset1 unchanged:", ch.peers[0].query("asset1"))
    print("  -> flagged ENDORSEMENT_POLICY_FAILURE: the tx IS in the block (ledger is immutable) but marked invalid;")
    print("     fix: collect an endorsement from a peer of Org2 as well.")

    print("\n=== Task 4b: troubleshoot - two concurrent txs on the same key (MVCC conflict) ===")
    ch.submit("TransferAsset", "asset1", "Carol", quiet=True)
    ch.submit("TransferAsset", "asset1", "Dave", quiet=True)
    res = ch.order_and_commit(quiet=True)
    print("  both simulated against version 2, ordered into one block ->", res)
    print("  first wins, second invalid (MVCC_READ_CONFLICT); owner now:", ch.peers[0].query("asset1")["owner"])
    print("  fix: client resubmits the second transaction (it will read the new version).")

    print("\n=== Task 4c: tampered endorsement is rejected ===")
    tx = ch.submit("TransferAsset", "asset1", "Eve", quiet=True)
    tx["endorsements"][1]["response"]["rwset"]["writes"]["asset1"]["owner"] = "Mallory"
    tx["rwset"] = tx["endorsements"][1]["response"]["rwset"]
    print("  result:", ch.order_and_commit(quiet=True), "(tampered endorsement disagrees with the other peer; its signature would also fail)")

    print("""
Transaction path: Proposal -> Endorsement (peers execute chaincode, sign rwset) ->
Ordering (orderer sequences txs into blocks, never executes them) -> Validation
(each peer checks endorsement policy + MVCC versions) -> Commit (block appended,
world state updated only for VALID txs; invalid txs stay on the ledger flagged).""")
