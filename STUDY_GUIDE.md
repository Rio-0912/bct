# Blockchain Labs – Complete Study Guide (from zero)

This guide assumes you only know the one-line definition: *"a blockchain is a chain of blocks that stores data."* It explains the theory first, then the tools, then every file in every lab, then a "if the examiner asks X, change Y" cheat sheet.

Contents
1. Theory you need
2. The tools and why each exists
3. How the repo is organised
4. Lab-by-lab walkthrough (what, why, every important line)
5. Examiner-modification cheat sheet
6. Git basics for this repo
7. Honest limitations

---

## 1. Theory you need

### 1.1 Blockchain in one paragraph
A blockchain is a list of **blocks**. Each block holds some **transactions** (like "Alice pays Bob 10") and the **hash of the previous block**. Because every block contains the fingerprint of the one before it, changing an old block breaks every block after it. Thousands of computers (**nodes**) each keep a copy and agree on which version is correct (**consensus**), so no single party can rewrite history.

### 1.2 Hash function (SHA-256)
A hash function turns any input into a fixed-size "fingerprint".
- `SHA-256("hello")` always gives the same 64 hex characters (256 bits).
- Change one letter and the whole output changes completely (**avalanche effect**).
- You cannot go backwards from the hash to the input (**one-way**).
- Two different inputs practically never give the same hash (**collision resistant**).

Used everywhere: block fingerprints, Merkle trees, mining, signatures.

### 1.3 Public/private keys and digital signatures
- You have a **private key** (secret number) and a **public key** (derived from it, shareable).
- To **sign** a message: you combine the message's hash with your private key to produce a **signature**.
- To **verify**: anyone with your public key, the message and the signature can check it is valid.
- Only the private key holder can make a valid signature, and any change to the message invalidates it.

This gives:
- **Authentication**: it really was that key holder.
- **Integrity**: the message wasn't changed.
- **Non-repudiation**: the signer can't deny signing.

Bitcoin and Ethereum use **ECDSA on the secp256k1 curve** (Lab 1 uses the same). Fabric uses ECDSA on the P-256 curve (Lab 9).

### 1.4 Merkle tree
A way to summarise many transactions into **one hash** (the **Merkle root**).
1. Hash each transaction (leaves).
2. Hash pairs of hashes together to form the next level.
3. Repeat until one hash remains: the root.

Why it matters:
- Any change in any transaction changes the root (tamper detection).
- To prove one transaction is in a block you only need the **sibling hashes along its path** (log2 N of them), not all transactions (**Merkle proof**). Light wallets rely on this.
- Updating one transaction only requires recomputing its path (log2 N + 1 hashes).

### 1.5 Block structure and hash linkage
Block = `index, timestamp, data, previous_hash, hash` (plus nonce in PoW). `hash = SHA256(all the other fields)`. Block N stores block N-1's hash. That is the "chain".

### 1.6 Proof of Work (PoW), nonce, difficulty, target
Problem: if anyone can add a block for free, an attacker could rewrite history cheaply. PoW makes adding a block expensive.
- Miners change a number called the **nonce** and re-hash the block until the hash is **below a target** (e.g. starts with several zeros).
- No shortcut exists: you must try many nonces. But checking a winning nonce takes one hash.
- **Difficulty** = how hard the target is. Smaller target = more leading zeros = more attempts.
- Each extra leading **hex** zero makes the target 16× smaller, so expected attempts grow about 16×.
- Bitcoin retargets difficulty every 2016 blocks to keep ~10 minutes per block.

To rewrite an old block the attacker must redo the PoW of that block and all later ones faster than the honest network – infeasible.

### 1.7 Consensus (how nodes agree)
- **PoW** (Bitcoin): most accumulated work wins.
- **Proof of Authority / Clique** (used in Lab 8): a fixed set of approved **signers** take turns producing blocks. Good for private networks.
- **Fabric (Lab 9)**: no mining. A permissioned network where selected peers **endorse** transactions and an **orderer** sequences them.

### 1.8 Ethereum concepts
- **Account**: an address (like `0xf39F…`). Two kinds: externally owned (controlled by a private key) and **contract accounts** (hold code).
- **Ether (ETH)** and **wei**: 1 ETH = 10^18 wei.
- **Transaction**: signed message from an account: send ETH and/or call a contract function. It has a **nonce** (the sender's counter, not the mining nonce), `to`, `value`, `data`, gas limit, gas price.
- **Gas**: the unit of computation cost. Every operation costs gas; you pay `gasUsed × gasPrice`. A plain ETH transfer costs exactly **21000 gas**. Gas stops infinite loops and spam.
- **Block, receipt**: miners/validators bundle transactions into blocks. A **receipt** is the result record of a transaction: `status` (1 success, 0 reverted), `blockNumber`, `gasUsed`, `logs` (events).
- **EVM**: the virtual machine every Ethereum node runs to execute contract code identically.
- **Revert**: if a `require(...)` fails, the whole transaction is undone (state changes rolled back); gas is still spent.
- **Event/log**: contracts can `emit` events recorded in the receipt, used by apps to track activity.
- **JSON-RPC**: the HTTP API a node exposes (e.g. `eth_getBalance`). Libraries like ethers.js call it for you.
- **Chain ID / network ID**: a number identifying the network (Hardhat = 31337, our private net = 1337).

### 1.9 Smart contract
A **smart contract** is a program stored on the blockchain at an address. Anyone can call its functions by sending a transaction; the code runs on every node, so the result is the same everywhere and cannot be altered once deployed.
- Written in **Solidity** (most common language), compiled to **bytecode** (what is deployed) and an **ABI** (a JSON description of its functions, so tools know how to call it).
- **State variables** are stored permanently on chain (e.g. a `balances` mapping).
- Functions can be **state-changing** (need a transaction and gas) or **view/read-only** (free to call locally).
- **Where used**: tokens (ERC-20), NFTs, DeFi (lending, exchanges), voting, supply-chain tracking, escrow, DAOs.
- **Deploy** = send a special transaction containing the bytecode; the network creates the contract at a new address.

### 1.10 Smart contract vulnerabilities (Lab 6)
- **Reentrancy**: a contract sends ETH to an external address *before* updating its own records. The receiver's code runs during that send and calls back into the contract while the records are still stale, repeating the withdrawal. (The 2016 DAO hack was this.)
  - **Fix**: *checks-effects-interactions* (update state first, then call out) and/or a **reentrancy guard**.
- **Missing access control**: a sensitive function with no check on who calls it. **Fix**: `require(msg.sender == owner)` or an `onlyOwner` modifier.
- Others you may be asked about: integer overflow (fixed by default since Solidity 0.8), unchecked return values, `tx.origin` misuse, front-running, bad randomness.

### 1.11 Public vs private/permissioned blockchains
- **Public** (Bitcoin, Ethereum mainnet): anyone joins, anonymous, PoW/PoS.
- **Private/permissioned** (our Lab 8 Geth network, Fabric): known participants, faster, no mining cost.

### 1.12 Hyperledger Fabric (Lab 9 theory)
Fabric is an enterprise permissioned blockchain. Key terms:
- **Organizations (Org1, Org2)**: members of the consortium. Each runs **peers**.
- **Peer**: node that holds the ledger and runs chaincode.
- **Channel**: a private sub-network/ledger shared by selected orgs.
- **Chaincode**: Fabric's name for smart contracts (Go/JS/Java).
- **World state**: the current value of every key (like a database); the **ledger** is the full history of blocks.
- **Orderer**: service that puts transactions into a global order and cuts blocks. It does **not** run chaincode.
- **Endorsement policy**: rule of who must approve a transaction, e.g. `AND(Org1, Org2)`.
- **Read/write set**: what keys a transaction read (with their versions) and wants to write.
- **MVCC check**: at commit, if a key read earlier has since changed, the transaction is invalid (`MVCC_READ_CONFLICT`).

**Transaction flow (memorise this):**
1. **Proposal**: client sends the request to endorsing peers.
2. **Endorsement**: each peer simulates the chaincode (without changing anything), signs the resulting read/write set, and returns it.
3. **Ordering**: client submits the endorsed transaction to the orderer, which sequences transactions into blocks.
4. **Validation**: every peer checks endorsement policy and MVCC versions.
5. **Commit**: block is appended; world state is updated for valid transactions only. Invalid ones stay in the block but are flagged.

---

## 2. The tools and why each exists

| Tool | What it is | Why we use it |
|---|---|---|
| **Python 3** | General programming language | Labs 1–4 (concepts), 8 (orchestration), 9 (simulation) |
| **`cryptography` (pip package)** | Python library for crypto | ECDSA keys/signatures in Labs 1 and 9 |
| **`hashlib`, `json`, `time`** | Python standard library | SHA-256, serialising blocks, timing |
| **Node.js** | Runs JavaScript outside the browser | Needed by Hardhat and ethers |
| **npm** | Node's package manager. `package.json` lists dependencies; `npm install` downloads them into `node_modules/`; `package-lock.json` pins exact versions | Labs 5–7 |
| **Solidity** | Smart contract language (`.sol` files) | Contracts in Labs 5–7 |
| **Hardhat** | Development framework for Ethereum: compiles Solidity (downloads the compiler), runs a built-in **local blockchain** in memory, and runs scripts against it. `hardhat node` starts that chain as a server on `http://127.0.0.1:8545`. | Labs 5, 6 (in-process chain), 7 (as a server) |
| **ethers.js (v6)** | JavaScript library to talk to Ethereum: providers (connect), signers (accounts that sign), contracts (call functions), utilities (`parseEther`) | Labs 5–7 |
| **Ganache** | An older local-blockchain tool; now deprecated | Lab 7 wording mentions it; we use `hardhat node` which does the same job |
| **Docker** | Runs programs in isolated "containers" from "images" so they behave the same everywhere | Lab 8 (Geth nodes) |
| **Geth (go-ethereum)** | The main Ethereum node software | Lab 8 – we used version 1.13.15 because it still supports Clique |
| **Clique** | Proof-of-Authority consensus in Geth | Lab 8 private network |
| **Git / GitHub** | Version control and hosting | Your repo `Rio-0912/bct` |

Hardhat built-in accounts: 20 test accounts with 10,000 fake ETH each. Their private keys are publicly known – **never use them on a real network**.

---

## 3. How the repo is organised

```
test/
  README.md                  quick run table
  STUDY_GUIDE.md             this file
  .gitignore                 files git must not track (node_modules, artifacts…)
  lab1_crypto_signatures/    lab1.py, requirements.txt, pdb.md, lab1.output.txt
  lab2_merkle_tree/          lab2.py, pdb.md, lab2.output.txt
  lab3_simple_blockchain/    lab3.py, pdb.md, lab3.output.txt
  lab4_proof_of_work/        lab4.py, pdb.md, lab4.output.txt
  lab5_solidity_contract/    contracts/SimpleBank.sol, scripts/lab5.js, hardhat.config.js, package.json, pdb.md
  lab6_vulnerability/        contracts/Vault.sol, scripts/lab6.js, hardhat.config.js, package.json, pdb.md
  lab7_ethers_ganache/       contracts/Token.sol, scripts/lab7.js, hardhat.config.js, package.json, pdb.md
  lab8_private_network/      lab8.py, pdb.md
  lab9_fabric_asset/         lab9.py, requirements.txt, pdb.md
```
- `pdb.md` = short run instructions + file explanation per lab.
- `*.output.txt` = saved output of a real run, useful as evidence.
- In Hardhat labs, `compile` creates `artifacts/` (compiled ABI + bytecode) and `cache/`. They are generated, so git ignores them.

---

## 4. Lab-by-lab walkthrough

### Lab 1 – Hashing and digital signatures (`lab1.py`)

**Goal:** show how a signature proves who sent a message and that it wasn't altered.

Code, function by function:
- `sha256_hex(data)`: `hashlib.sha256(data.encode()).hexdigest()`. `.encode()` converts the string to bytes (hash functions work on bytes); `.hexdigest()` shows the 32-byte result as 64 hex characters.
- `sign(private_key, message)`: `private_key.sign(message_bytes, ec.ECDSA(hashes.SHA256()))`. The library hashes the message with SHA-256 and signs the hash with ECDSA. Returns signature bytes.
- `verify(public_key, message, signature)`: calls `public_key.verify(...)`. That function **raises** `InvalidSignature` if wrong, returns nothing if right; we wrap it in `try/except` to return `True`/`False`.
- Main:
  - `ec.generate_private_key(ec.SECP256K1())` creates the key pair on the Bitcoin/Ethereum curve; `priv.public_key()` derives the public key.
  - `public_bytes(PEM, SubjectPublicKeyInfo)` just prints the public key in a standard text format.
  - Task 3: verify with the original message → `True`.
  - Task 4: change "5 BTC" → "500 BTC", verify with the **same signature** → `False`.

**Explanation to give the examiner:** the signature is bound to the hash of the exact message. The new message has a totally different hash, so the signature doesn't match. This is why nobody can alter a transaction after it was signed, and why only the key owner can authorise spending.

Note: ECDSA signatures include randomness, so the signature differs each run, but verification still works.

### Lab 2 – Merkle tree (`lab2.py`)

**Goal:** build a tree over 8 transactions, update one, recompute only its path.

- `h(s)`: SHA-256 hex helper.
- `build_tree(leaves)`: keeps `levels`, a list of lists. Starts with leaf hashes. While more than one node: if the count is odd it **duplicates the last node** (Bitcoin's rule), then each parent = `h(left + right)` (string concatenation of two hex hashes). Returns all levels; `levels[-1][0]` is the root.
- `update_leaf(levels, index, new_tx)`: the **selective recomputation**. Recompute the leaf hash, then climb: find the pair (`index - index%2` is the left sibling's position), compute the parent, set `index //= 2`, repeat. Counts hashes: 4 for 8 leaves (1 leaf + 3 parents) versus 15 nodes in a full rebuild.
- `proof(levels, index)`: collects the sibling at each level plus whether it is on the left. `verify_proof` rebuilds the root from the transaction and those siblings.
- Main flow: hash 8 txs → build/print → change `txs[2]` → `update_leaf` → `assert` that the result equals a full rebuild (proves the shortcut is correct) → print which node indices changed at each level (only one per level) → compare roots → show proof passes for the new tx and fails with the old tx.

**Explanation:** a change to one leaf changes only the nodes above it, but the root always changes, so comparing one root detects tampering in any of N transactions. Verifying one transaction needs only log2(N) hashes – "efficient integrity verification".

### Lab 3 – Simple blockchain (`lab3.py`)

- `Block.__init__`: stores fields and computes `self.hash`.
- `compute_hash`: dumps `index, timestamp, data, previous_hash` to JSON with `sort_keys=True` (so the same data always serialises identically) and SHA-256 hashes it. The stored `hash` is deliberately **not** included (a hash can't contain itself).
- `Blockchain.__init__`: genesis block (index 0, previous hash `"000…0"`).
- `add_block(data)`: new block gets `previous_hash = last.hash`.
- `validate()`: for every block, (1) recompute its hash and compare to the stored one – catches edited content; (2) compare `previous_hash` to the previous block's actual hash – catches broken links.
- Main demonstrates three attacks:
  1. Edit data only → check 1 fails at that block.
  2. Edit data and fix that block's hash → block 1 is internally consistent, but block 2's `previous_hash` no longer matches → check 2 fails at block 2.
  3. Re-hash and re-link **every** later block → the chain validates again. That's the lesson: linkage alone isn't enough in a real network; **PoW/consensus** (Lab 4) makes redoing all blocks computationally impossible, and other nodes would reject your version anyway.

**Effect on subsequent blocks:** the modified block's hash changes → the next block's stored `previous_hash` is stale → mismatch cascades down the chain.

### Lab 4 – Proof of Work (`lab4.py`)

- `mine(data, prev, difficulty)`: builds `prefix = "0" * difficulty`; loops `nonce = 0,1,2…`; hashes `prev + data + nonce`; stops when the hex digest starts with the prefix. Returns nonce, hash, attempts (nonce+1) and elapsed time (`time.perf_counter`).
- `mine_target(data, prev, target)`: the same search but compares `int(hash, 16) < target`. Because a hex digit is 4 bits, `d` leading zero hex digits = `4d` leading zero bits = target `2^(256-4d)`.
- Main: mine at difficulty 4 (our run: nonce 34370, 34371 attempts), then difficulties 1–6 in a table, then target view.

Observed behaviour: attempts grow roughly 16× per level (the exact numbers are luck-dependent, but the trend is exponential). Time is proportional to attempts.

**Relationship to state:** `probability per try = target / 2^256`; `expected attempts = 2^256 / target`. Smaller target → higher difficulty → more attempts → more time/energy.

### Lab 5 – Solidity contract with Hardhat (`SimpleBank.sol`, `lab5.js`)

**`SimpleBank.sol`, line by line:**
- `// SPDX-License-Identifier: MIT`: licence tag (compiler warns if absent).
- `pragma solidity ^0.8.20;`: allowed compiler versions.
- `contract SimpleBank { … }`: like a class. When deployed it becomes an on-chain object with an address.
- `address public owner;`: `public` auto-creates a getter function. `address` = an account.
- `uint256 public minDeposit = 0.01 ether;`: unsigned 256-bit integer; `ether` is a unit suffix (10^18 wei).
- `mapping(address => uint256) public balances;`: key-value storage (address → amount).
- `event Deposited(address indexed user, uint256 amount);`: declares a log type; `indexed` makes it searchable.
- `constructor() { owner = msg.sender; }`: runs once at deployment; `msg.sender` is who called/deployed.
- `deposit() external payable`: `payable` lets the call carry ETH (`msg.value`). `require(cond, "message")` reverts everything if false. Then credits `balances[msg.sender]` and `emit`s the event.
- `withdraw(amount)`: checks balance, subtracts first, then sends via `payable(msg.sender).call{value: amount}("")`, and requires success. (Safe order; compare to Lab 6.)
- `setMinDeposit(v)`: only the owner (`require(msg.sender == owner, "Only owner")`). This is the **access control** example and the "business rule" an examiner may ask you to change.
- `getBalance(address)`: `view` = read-only, no gas when called off-chain.

**`lab5.js`:**
- `const hre = require("hardhat")` / `ethers`: Hardhat injects ethers and a built-in in-memory chain; running with `npx hardhat run` starts that chain for the duration of the script.
- `getSigners()`: returns the 20 test accounts; `owner` = first, `user` = second.
- `getContractFactory("SimpleBank")`: loads the compiled ABI+bytecode from `artifacts/`. `.deploy()` sends the deployment transaction. `deploymentTransaction().wait()` waits until it's mined and returns the receipt (block number, gas).
- `bank.connect(user).deposit({ value: parseEther("1") })`: calls the function **as** `user`, attaching 1 ETH. `tx.wait()` → receipt.
- Reads `balances` via `getBalance` (a read call), prints `status` (1 = success), `blockNumber`, `gasUsed` (47,329 in our run), and decodes events with `interface.parseLog`.
- Task 4: shows a 0.5 ETH deposit works while `minDeposit` is 0.01, then owner sets 2 ETH, then 0.5 ETH fails ("Deposit below minimum"), 2.5 ETH works, and a non-owner call to `setMinDeposit` fails ("Only owner").

**Terms:** *compile* (Solidity → bytecode+ABI), *deploy* (put on chain), *transact* (state change, costs gas), *call* (read, free).

### Lab 6 – Vulnerability analysis (`Vault.sol`, `lab6.js`)

Three contracts in one file:

**`VulnerableVault`**
```solidity
function withdraw(uint256 amount) external {
    require(balances[msg.sender] >= amount, "Insufficient balance");
    (bool ok, ) = msg.sender.call{value: amount}("");  // 1. send ETH first
    require(ok, "Transfer failed");
    unchecked { balances[msg.sender] -= amount; }       // 2. update balance last  <-- BUG
}
function sweep() external { payable(msg.sender).transfer(address(this).balance); }  // anyone can call
```
Bug 1 (reentrancy): `msg.sender.call{value}` hands control to the receiver. If the receiver is a contract, its `receive()` function runs *right then*, while `balances` is still unchanged, and can call `withdraw` again – passes the balance check again – repeat until the vault is empty. (`unchecked` stops Solidity 0.8 from reverting on the underflow that would otherwise happen at the end – it lets the exploit complete; without it, the final subtraction would revert the whole attack.)
Bug 2 (access control): `sweep()` has no restriction.

**`SecureVault` (the fix)**
- `withdraw`: balance reduced **before** the external call (checks-effects-interactions). A re-entrant call now sees the reduced balance and fails the `require`.
- `nonReentrant` modifier: a `_lock` variable set to 2 during execution; a nested call hits `require(_lock == 1, "Reentrancy blocked")`. `_;` in a modifier marks where the function body runs.
- `onlyOwner` on `sweep`, and funds go to `owner`.

**`Attacker`**
- `attack()`: deposits 1 ETH then withdraws 1 ETH.
- `receive() external payable`: special function called when the contract receives plain ETH. It checks the vault still has ≥ `amount` and withdraws again – the re-entry loop.

**`lab6.js` tests** (a tiny home-made test harness: `check(name, condition)` prints PASS/FAIL):
- Task 1: normal deposit/withdraw works on the vulnerable vault.
- Task 2: setup puts 10 ETH from two honest users; attacker deposits 1 ETH; vault goes 10 → 0, attacker holds 11. Also a random account calls `sweep()` and empties it.
- Tasks 3/4 on `SecureVault`: *positive tests* (legit withdraw, owner sweep succeed) and *negative/security tests* (attack tx reverts, vault still has 10 ETH, attacker has 0, non-owner sweep reverts "Only owner", over-withdraw reverts).
- `reverts(promise, msg)`: awaits a call expecting it to throw, and checks the message.

Why "positive and negative": the examiner wants proof that the fix didn't break normal use *and* that the attack no longer works.

### Lab 7 – Local Ethereum with ethers.js (`lab7.js`, `Token.sol`)

Difference from Lab 5: here the chain is a **separate running server** (`npx hardhat node`) and the script is **plain Node/ethers** that connects over **JSON-RPC** at `http://127.0.0.1:8545` – exactly how a real app talks to Ethereum (or to Ganache).

`lab7.js` section by section:
- `JsonRpcProvider(RPC)`: read-only connection. `getNetwork()` → chainId 31337. `listAccounts()` → signers for the node's unlocked accounts. `getBalance` → 10,000 ETH each.
- Ether transfer: `sender.sendTransaction({to, value})` then `wait()`. `printReceipt` shows `hash, from, to, blockNumber, status, gasUsed` (21000 for plain transfer), `gasPrice`, `fee = gasUsed × gasPrice`, `value`.
- The receiver balance is read at block `n-1` and block `n` explicitly. (A first version read "latest" twice and ethers returned a cached value, showing a false 0 change. Reading by block number fixes this.)
- Token: loads ABI/bytecode from `artifacts/…/SimpleToken.json`, `ContractFactory(abi, bytecode, signer).deploy(1000)`, calls `token.transfer(receiver, 250)`, decodes the `Transfer` event from `receipt.logs`, shows balances 750/250.
- Final: transfer more than the balance → the node rejects it with "Insufficient token balance".
- Task 4 changes via environment variables: `VALUE` (ETH amount) and `TO_INDEX` (which account receives); `RPC_URL` to point elsewhere.

`Token.sol` is a minimal token: `balanceOf` mapping, constructor gives the deployer the whole supply, `transfer` moves tokens and emits `Transfer`.

Key vocabulary for the exam: *provider* (read access), *signer* (can sign/send), *receipt* (result of a mined tx), *tx hash* (ID), *gas used vs gas limit*, *nonce* (sender's tx counter).

### Lab 8 – Private Ethereum network, 3 nodes (`lab8.py`)

**Concept:** run three independent Ethereum nodes that share the same **genesis block** and **network ID** so they form their own private chain, separate from mainnet.

`lab8.py`:
- `sh(...)`: runs a command, raises on failure. `js(i, expr)`: runs `geth attach --exec "<js>"` inside container *i* to ask the node something (like `net.peerCount`).
- `setup()`:
  1. Creates a Docker network `lab8net` (172.30.0.0/24) so containers get fixed IPs.
  2. For each node: a Docker **volume** (persistent data folder), a password file, and `geth account new` → one account per node.
  3. Builds `genesis.json`: `chainId 1337`; all fork blocks 0 (all features active from start); `clique: {period: 2, epoch: 30000}` (a block every 2 s); `extradata` = 32 zero bytes + the three signer addresses + 65 zero bytes (this is how Clique lists the initial authorised signers); `alloc` gives two accounts 1000 ETH; `gasLimit` 8,000,000.
  4. `geth init` writes the genesis into each node's data directory – "preinitialised".
  5. Starts containers with flags: `--networkid 1337`, `--nodiscover` (don't search for strangers), `--http … --http.api eth,net,web3,admin,clique,txpool`, `--unlock <acct> --password …` (so the node can sign), `--mine --miner.etherbase <acct>` (this node produces blocks), `--nat extip:<ip>`, `--syncmode full`.
- `connect_all()`: gets node1's **enode URL** (its network identity, `enode://<pubkey>@ip:port`) and calls `admin.addPeer(...)` from nodes 2 and 3; node2↔node3 as well.
- `main()`:
  - Task 1: `docker ps` shows three containers up.
  - Task 2: `net.peerCount` = 2 on each, **identical genesis hash** (proves same network), same network ID, `admin.peers`, `clique.getSigners()` lists three signers.
  - Task 3: `eth.sendTransaction` on node1 (5 ETH to node3's account) → wait → ask **node3** for the transaction, receipt (`status 0x1`), recipient balance, and compare the same block's hash on node1/node3 (identical).
  - Task 4: `docker stop lab8-node3` → node1's `peerCount` falls to 1 → send another tx → chain still advances (Clique needs a majority of signers, 2 of 3) → `docker start lab8-node3` → it has too few peers (`--nodiscover`) → `addPeer` again → it **syncs** and its block number catches up with node1.

Troubleshooting cheat-sheet for this lab:
| Symptom | Likely cause | Fix |
|---|---|---|
| `peerCount` 0 | nodes never connected / `--nodiscover` | `admin.addPeer(enode)` |
| Peers connect then drop | different `networkid` or genesis hash | re-init with the same genesis, same `--networkid` |
| Blocks stop | fewer than majority of signers online or signer not unlocked | start nodes / unlock |
| Tx stays pending | no node mining, or nonce/funds issue | check `eth.mining`, balance |
| Node on wrong chain | different data directory/genesis | wipe volume, `geth init` again |

Commands: `python lab8.py` runs all; `python lab8.py cleanup` deletes the containers, volumes, network. Docker Desktop must be running. Why Geth 1.13.x: newer Geth removed Clique block production.

### Lab 9 – Fabric asset transaction (`lab9.py`)

**Important:** this is a **Python simulation** that mirrors Fabric's logic. A real Fabric network (Docker images, `fabric-samples/test-network`, `peer chaincode invoke` commands) was not set up, because downloading and running the remote install script was blocked in this session. In an exam with real Fabric, the commands will be different, but the concepts are identical.

Classes:
- `Identity`: wraps a P-256 key; `sign(payload)` signs JSON of the payload. `verify(pub, payload, sig)` checks.
- `Chaincode.invoke(state, fn, args)`: the asset logic. It does **not** modify state; it returns `(result, writes, reads)`, where `reads` records the **version** of each key it read. Functions: `CreateAsset` (fails if the ID exists), `TransferAsset` (changes owner), `UpdateAsset` (colour/size), `ReadAsset`.
- `Peer`: has its own `state` (world state: `key → {value, version}`) and `ledger` (blocks).
  - `endorse(proposal)`: runs the chaincode on its current state, builds the response with the read/write set and **signs it**. State untouched.
  - `validate_and_commit(block, policy_orgs)`: for each tx in the block: verify each endorsement signature; check all endorsements carry the same read/write set; check the set of endorsing orgs ⊇ the required orgs (**policy**); check each key's current version == version read (**MVCC**). If everything is OK it writes values and increments versions; otherwise it records a flag (`ENDORSEMENT_POLICY_FAILURE`, `MVCC_READ_CONFLICT`, …).
- `Orderer`: collects transactions, `cut_block()` makes a block `{number, prev_hash, data_hash, txs}` and chains it with a hash. It never looks at chaincode.
- `Channel`: two peers (Org1, Org2), one orderer, policy `{Org1, Org2}`. `submit()` = Proposal + Endorsement; `order_and_commit()` = Ordering + Validation + Commit, printing numbered steps 1–5 so the flow is visible.

Main flow:
1. Task 1: list channel, orgs, peers, policy.
2. Task 2: create `asset1` (owner Tomoko), query it.
3. Task 3: transfer to Brad; both peers' world state shows owner Brad, version 2; ledger height 2.
4. Task 4a: endorsement by Org1 only → block still created but tx flagged `ENDORSEMENT_POLICY_FAILURE`; asset unchanged. **Fix:** also get Org2's endorsement.
5. Task 4b: two transfers prepared at the same time against version 2 → in one block, first `VALID`, second `MVCC_READ_CONFLICT`. **Fix:** resubmit after re-reading.
6. Task 4c: modify an endorsement's content → rejected (`ENDORSEMENT_MISMATCH`/bad signature).

Real-Fabric equivalents you may meet in an exam (for orientation only; not run here): `./network.sh up createChannel -c mychannel -ca`, `./network.sh deployCC …`, `peer chaincode invoke … -c '{"function":"CreateAsset","Args":[…]}'`, `peer chaincode query … -c '{"Args":["ReadAsset","asset1"]}'`, environment variables like `CORE_PEER_LOCALMSPID=Org1MSP` to act as an org.

---

## 5. Examiner-modification cheat sheet

| Lab | "Examiner says…" | Do this |
|---|---|---|
| 1 | different message | edit `tx = "…"` in `lab1.py`, rerun |
| 1 | tamper differently | edit `tampered = "…"` |
| 2 | different transactions / count | edit the `txs` list (any count; odd counts duplicate the last node) |
| 2 | modify another transaction | change the index in `txs[2] = …` **and** `update_leaf(levels, 2, …)` (use the same index in `proof(levels, 2)` and the old-tx check) |
| 3 | add more blocks | add strings to the `for d in [...]` list |
| 3 | tamper another block | change `bc.chain[1]` to `bc.chain[k]` in the three tamper steps |
| 4 | change difficulty | change `4` in `mine(data, prev, 4)` or `range(1, 7)` |
| 4 | change data | edit `data` |
| 4 | change target directly | pass your own target, e.g. `mine_target(data, prev, 1 << 236)` (= difficulty 5). Remember: **smaller target = harder**, so `1 << 232` is harder than `1 << 236` |
| 5 | change the rule | edit `minDeposit = 0.01 ether` in `SimpleBank.sol` (or call `setMinDeposit`), then `npx hardhat compile` and rerun. Other typical edits: add `maxWithdraw`, restrict `deposit` to an allow-list mapping, make `withdraw` owner-only |
| 5 | redeploy | `npm run compile && npm start` (each run starts a fresh chain and redeploys) |
| 6 | different vulnerability | e.g. remove `onlyOwner` or reorder `withdraw`; fix with the matching pattern; add a test line via `check("…", …)` |
| 7 | other account/value | `VALUE=2 TO_INDEX=3 node scripts/lab7.js` (PowerShell: `$env:VALUE=2; $env:TO_INDEX=3; node scripts/lab7.js`) |
| 7 | different contract call | change `token.transfer(receiver.address, 250)` |
| 7 | different RPC | `RPC_URL=http://host:port` |
| 8 | stop a node | `docker stop lab8-node2` etc.; restart with `docker start`; reconnect with `admin.addPeer` |
| 8 | check status manually | `docker exec lab8-node1 geth attach --exec "net.peerCount" /root/.ethereum/geth.ipc` (Git Bash: prefix `MSYS_NO_PATHCONV=1`) |
| 9 | change the policy | `self.policy = {"Org1"}` in `Channel.__init__` |
| 9 | different asset operation | change the `ch.submit("TransferAsset", …)` lines |

After editing any `.sol` file you must **recompile** (`npx hardhat compile`, or `npm run compile`). After editing Python/JS you just rerun.

---

## 6. Git basics for this repo

- `git status` shows changes. `git add -A` stages all. `git commit -m "message"` saves a snapshot locally. `git push` uploads to GitHub (`origin`, branch `main`).
- `.gitignore` lists files git skips (`node_modules/`, `artifacts/`, `cache/`, `*.log`) because they can be regenerated.
- To get the project on another machine: `git clone https://github.com/Rio-0912/bct.git`, then in each Node lab `npm install --legacy-peer-deps`, and `pip install -r requirements.txt` in Labs 1 and 9.
- `--legacy-peer-deps` is needed because some Hardhat plugin versions declare conflicting peer dependency versions.

---

## 7. Honest limitations

- **Lab 9 is a simulation**, not a real Fabric network. It is a good model for explaining the transaction flow but would not satisfy a task that requires running real `peer` commands.
- **Lab 7** uses `hardhat node` instead of Ganache (Ganache is discontinued). The ethers script is the same.
- **Lab 8** uses Clique PoA with Geth 1.13.15, not PoW; the private-network concepts (genesis, network ID, peers, enode, sync) are the same.
- Hardhat's test accounts and the passwords used in Lab 8 are for learning only.
- Hash outputs and timings differ between machines; the *behaviour* (valid → invalid, root changes, 16× effort) is what matters.
