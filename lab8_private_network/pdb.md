# Lab 8 – Private Ethereum Network (3 Nodes)

## 0. One-time setup (start here if you only copy-pasted the code)

### Prerequisites
| Need | Check with | If missing |
|---|---|---|
| Python 3.9+ | `python --version` | python.org |
| Docker Desktop (Windows needs the WSL2 backend) | `docker --version` | docker.com; **start Docker Desktop and wait until it says running** |
| Docker daemon actually running | `docker info` (must print "Server Version") | open Docker Desktop; the error "cannot find the file specified ... dockerDesktopLinuxEngine" means it is not started |
| Internet, once | - | first run pulls the image (~100 MB) |
| ~1 GB free disk and a free subnet `172.30.0.0/24` | `docker network ls` | change `SUBNET`/`NODES` in `lab8.py` if it clashes |

### Dependencies
No `pip install` and no `package.json` - the script uses only Python's standard library and calls the `docker` command. Geth runs *inside* Docker, so you do not install it.

Pull the image ahead of time (so the exam run needs no internet):
```
docker pull ethereum/client-go:v1.13.15
```
Use exactly `v1.13.15` (or any 1.13.x): Geth 1.14+ removed Clique block production, so nodes would not mine.

### What gets created (and how to reset)
The script creates containers `lab8-node1..3`, volumes `lab8-data1..3` (each node's chain data and account key) and a Docker network `lab8net`. `lab8.py` deletes old ones at the start, so reruns are safe. To clean manually:
```
python lab8.py cleanup
```

### Common errors
| Error | Fix |
|---|---|
| `failed to connect to the docker API` | Docker Desktop is not running - start it, wait 30-60 s |
| Git Bash path mangling (`C:/Program Files/Git/root/.ethereum`) | prefix with `MSYS_NO_PATHCONV=1 python lab8.py`, or use PowerShell |
| `Pool overlaps with other one on this address space` | another Docker network uses 172.30.0.0/24; change `SUBNET` and the `NODES` IPs at the top of `lab8.py` |
| `peerCount` is 0 | nodes need `admin.addPeer(enode)` (the script does it); check same `networkid` and genesis |
| `pull access denied` / timeout | no internet; run `docker pull` when online |

&nbsp;

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
