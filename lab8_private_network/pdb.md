# Lab 8 – Private Ethereum Network (3 Nodes)

## How to run
Requires Python 3 and **Docker Desktop running**. The first run pulls the `ethereum/client-go:v1.13.15` image. It takes about 1–2 minutes.

```
cd lab8_private_network
python lab8.py            # creates the network and runs all 4 tasks
python lab8.py cleanup    # removes containers, volumes and network
```

On Git Bash, prefix with `MSYS_NO_PATHCONV=1`. A saved run is in `lab8.output.txt`.

&nbsp;

## Files and key components

**`lab8.py`**
- `setup()` – creates a Docker network (`172.30.0.0/24`), one volume per node, one account per node, a shared **genesis.json** (chain ID 1337, Clique proof-of-authority, 2-second blocks, all 3 accounts as signers), runs `geth init` on each, then starts three containers `lab8-node1..3` with fixed IPs, mining and unlocked accounts.
- `connect_all()` – nodes run with `--nodiscover`, so peers are linked manually with `admin.addPeer(enode)`.
- `js(i, expr)` – runs a JavaScript expression in node *i*'s Geth console (`docker exec ... geth attach --exec`).
- `main()` – the tasks:
  1. **Start** nodes and list them.
  2. **Verify network**: each node's `peerCount`, same genesis hash, same network ID, signer list.
  3. **Transaction**: send 5 ETH from node1's account, read the transaction, receipt and recipient balance from node3, and compare the same block hash on node1 and node3.
  4. **Fault**: stop node3. The peer count drops and the chain keeps producing blocks (2 of 3 signers is a majority). Restart node3, re-add its peers, and it syncs back to the head.

**Why re-adding peers is needed:** with `--nodiscover` a restarted node doesn't find peers on its own. A mismatched `--networkid` or genesis would make the handshake fail (peer count stays 0).

**`lab8.output.txt`** – saved output.
