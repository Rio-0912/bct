# Lab 9 – Hyperledger Fabric Asset Transaction

## 0. One-time setup (start here if you only copy-pasted the code)

### Prerequisites
| Need | Check with | If missing |
|---|---|---|
| Python 3.9+ | `python --version` (on Mac/Linux use `python3`) | install from python.org; on Windows tick **"Add python.exe to PATH"** |
| pip | `python -m pip --version` | comes with Python |

### Install the dependency
```
cd lab9_fabric_asset
pip install -r requirements.txt
```
or `pip install cryptography`. Nothing else is needed: this lab is a Python simulation, so there is **no Docker, no Fabric binaries and no `package.json`**.

### If your exam uses REAL Hyperledger Fabric (not this simulation)
You would need Docker Desktop running, Git, `curl`, and on Windows a Linux-like environment (WSL2 Ubuntu is the supported route). The official sequence from the Fabric docs, shown for orientation only (it was not run in this project):
```
curl -sSLO https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/install-fabric.sh && chmod +x install-fabric.sh
./install-fabric.sh docker samples binary
cd fabric-samples/test-network
./network.sh up createChannel -c mychannel -ca
./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-go -ccl go
```
It downloads several GB of Docker images, so do it in advance with internet.

### Common errors
| Error | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'cryptography'` | `python -m pip install cryptography` |

&nbsp;

> **Note:** this is a pure-Python **simulation** of Fabric's execute–order–validate flow. It is not a real Fabric network and uses no Docker or Fabric binaries.

## How to run
Requires Python 3 and the `cryptography` package (`pip install -r requirements.txt`).

```
cd lab9_fabric_asset
python lab9.py
```

A saved run is in `lab9.output.txt`.

&nbsp;

## Files and key components

**`lab9.py`**
- `Identity` / `verify` – each peer has a P-256 ECDSA key (as Fabric does) and signs its endorsements.
- `Chaincode.invoke()` – the asset-transfer logic: `CreateAsset`, `ReadAsset`, `TransferAsset`, `UpdateAsset`. It runs against a snapshot and returns a **read/write set** (keys read with their versions, keys to write).
- `Peer`
  - `endorse()` – **Endorsement**: simulates the chaincode and signs the result without changing state.
  - `validate_and_commit()` – **Validation + Commit**: checks signatures, that all endorsers agree, the **endorsement policy**, and **MVCC** version checks; valid transactions update the world state, invalid ones are only flagged in the block.
- `Orderer` – **Ordering**: sequences transactions into hash-chained blocks without executing them.
- `Channel` – ties together Org1 and Org2 peers, the orderer and the policy `AND(Org1, Org2)`; `submit()` does Proposal + Endorsement, `order_and_commit()` does the rest.
- `__main__` – the tasks:
  1. Show the channel, orgs and peers.
  2. Create `asset1` and query it.
  3. Transfer it to Brad and show both peers' world state (version 2).
  4. Troubleshooting: (a) endorsed by only one org → `ENDORSEMENT_POLICY_FAILURE`; (b) two writes to the same key → second gets `MVCC_READ_CONFLICT`; (c) tampered endorsement is rejected.

**Transaction path:** Proposal → Endorsement → Ordering → Validation → Commit.

**`lab9.output.txt`** – saved output.
