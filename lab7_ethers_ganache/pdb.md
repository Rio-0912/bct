# Lab 7 – Local Ethereum with Ethers.js

## How to run
Requires Node.js; dependencies are in the repo root `node_modules`. Ganache is deprecated, so `hardhat node` is used as the local RPC endpoint (same role).

Terminal 1 – start the local node:
```
cd lab7_ethers_ganache
npx hardhat compile
npx hardhat node
```

Terminal 2 – run the script:
```
cd lab7_ethers_ganache
node scripts/lab7.js
```

Task 4 (change account or value) – use environment variables:
```
VALUE=3 TO_INDEX=2 node scripts/lab7.js        # Git Bash
$env:VALUE=3; $env:TO_INDEX=2; node scripts/lab7.js   # PowerShell
```
`RPC_URL` can point to another endpoint. A saved run is in `lab7.output.txt`.

&nbsp;

## Files and key components

**`scripts/lab7.js`** (plain ethers v6, no Hardhat runtime)
- Connects with `JsonRpcProvider`, prints chain ID, block number, and the first 5 accounts with balances (Task 1).
- Sends an Ether transfer from account 0 to account `TO_INDEX` (Task 2a).
- `printReceipt()` – prints hash, from, to, block, status, gas used, gas price, fee, value (Task 3).
- Receiver balance is read at the receipt's block and the block before it, which gives the exact change.
- Deploys the token, calls `transfer(receiver, 250)`, decodes the `Transfer` event and shows both balances (Task 2b).
- Final section sends an over-balance token transfer to show the revert reason (Task 4).

**`contracts/Token.sol`** – minimal ERC-20-like `SimpleToken`: `balanceOf`, `transfer` (reverts with "Insufficient token balance"), `Transfer` event.

**`hardhat.config.js`** – Solidity 0.8.20; compiling creates `artifacts/`, which the script reads for the ABI and bytecode.

**`lab7.output.txt`** – saved output.
