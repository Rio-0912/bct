# Lab 5 – Solidity Smart Contract Development

## How to run
Requires Node.js. Dependencies (Hardhat, ethers) live in the repo root `node_modules` – run `npm install --legacy-peer-deps` in the repo root if missing.

```
cd lab5_solidity_contract
npx hardhat compile
npx hardhat run scripts/lab5.js
```

Hardhat's built-in local blockchain is used, so no separate node is needed. A saved run is in `lab5.output.txt`.

&nbsp;

## Files and key components

**`contracts/SimpleBank.sol`**
- `owner`, `minDeposit`, `balances` – state variables. `minDeposit` is the business rule changed in Task 4.
- `deposit()` – payable; reverts below `minDeposit`; updates the sender's balance; emits `Deposited`.
- `withdraw(amount)` – checks balance, updates state, then sends Ether.
- `setMinDeposit(v)` – access control: only `owner` may call it (`require(msg.sender == owner)`).
- `getBalance(user)` – read-only query.

**`scripts/lab5.js`** – deploys and runs the tasks: deploy (address, block, gas), deposit 1 ETH (state change), read balance, print receipt (hash, status, block, gas, event), then raise `minDeposit` to 2 ETH and show a 0.5 ETH deposit now reverts while 2.5 ETH works, and a non-owner is rejected.

**`hardhat.config.js`** – Solidity version 0.8.20 and an optional `localnode` network entry.

**`lab5.output.txt`** – saved output.
