# CS413 Blockchain Labs (9 labs, one folder each)

Saved output of each run is in `labN*.output.txt` next to each script.

| Lab | Run | Notes |
|---|---|---|
| 1 | `python lab1_crypto_signatures/lab1.py` | SHA-256 + ECDSA secp256k1 |
| 2 | `python lab2_merkle_tree/lab2.py` | Merkle root, path-only recompute |
| 3 | `python lab3_simple_blockchain/lab3.py` | chain + validation + tamper |
| 4 | `python lab4_proof_of_work/lab4.py` | PoW, difficulty 1-6, target view |
| 5 | `cd lab5_solidity_contract && npx hardhat compile && npx hardhat run scripts/lab5.js` | Solidity bank contract |
| 6 | `cd lab6_vulnerability && npx hardhat run scripts/lab6.js` | reentrancy + access control, fix, tests |
| 7 | `cd lab7_ethers_ganache && npx hardhat node` (terminal 1), `node scripts/lab7.js` (terminal 2) | env: `VALUE`, `TO_INDEX`, `RPC_URL` |
| 8 | `cd lab8_private_network && python lab8.py` (Docker running); `python lab8.py cleanup` | 3 geth nodes, Clique PoA |
| 9 | `python lab9_fabric_asset/lab9.py` | Python SIMULATION of Fabric flow (not a real Fabric network) |

Labs 5-7 each have their own `package.json`: run `npm install --legacy-peer-deps` inside the lab folder first. Labs 1 and 9 have a `requirements.txt` (`pip install -r requirements.txt`); the other Python labs use only the standard library, and Lab 8 needs Docker.
Lab 7 uses `hardhat node` as the local RPC in place of Ganache (Ganache is deprecated).
