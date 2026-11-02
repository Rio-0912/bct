// Lab 7: plain ethers.js (v6) against a local JSON-RPC endpoint (default http://127.0.0.1:8545)
const { ethers } = require("ethers");
const fs = require("fs");
const RPC = process.env.RPC_URL || "http://127.0.0.1:8545";
const VALUE = process.env.VALUE || "1.5";        // Task 4: change these
const TO_INDEX = Number(process.env.TO_INDEX || 1);

function printReceipt(label, tx, rc) {
  console.log(`--- Receipt: ${label}`);
  console.log("  tx hash    :", rc.hash);
  console.log("  from       :", rc.from);
  console.log("  to         :", rc.to);
  console.log("  block      :", rc.blockNumber);
  console.log("  status     :", rc.status === 1 ? "1 (success)" : "0 (reverted)");
  console.log("  gas used   :", rc.gasUsed.toString(), "| gas price:", rc.gasPrice.toString(), "| fee(wei):", (rc.gasUsed * rc.gasPrice).toString());
  console.log("  value (wei):", tx.value.toString());
}

(async () => {
  const provider = new ethers.JsonRpcProvider(RPC);
  console.log("=== Task 1: connect ===");
  const net = await provider.getNetwork();
  console.log("RPC:", RPC, "| chainId:", net.chainId.toString(), "| block:", await provider.getBlockNumber());
  const accounts = (await provider.listAccounts()).slice(0, 5);
  for (const a of accounts) console.log(" ", a.address, ethers.formatEther(await provider.getBalance(a.address)), "ETH");

  console.log("\n=== Task 2a: Ether transfer ===");
  const sender = accounts[0], receiver = accounts[TO_INDEX];
    const tx = await sender.sendTransaction({ to: receiver.address, value: ethers.parseEther(VALUE) });
  const rc = await tx.wait();
  printReceipt("Ether transfer", tx, rc);
  // read at explicit block numbers (avoids provider-side caching of "latest")
  const before = await provider.getBalance(receiver.address, rc.blockNumber - 1);
  const after = await provider.getBalance(receiver.address, rc.blockNumber);
  console.log("  receiver balance:", ethers.formatEther(before), "->", ethers.formatEther(after), "ETH (change", ethers.formatEther(after - before) + ")");

  console.log("\n=== Task 2b: smart-contract transaction (ERC20-like token) ===");
  const art = JSON.parse(fs.readFileSync("artifacts/contracts/Token.sol/SimpleToken.json"));
  const factory = new ethers.ContractFactory(art.abi, art.bytecode, sender);
  const token = await factory.deploy(1000);
  await token.waitForDeployment();
  console.log("token at", await token.getAddress());
  const ttx = await token.transfer(receiver.address, 250);
  const trc = await ttx.wait();
  printReceipt("token.transfer(250)", ttx, trc);
  const ev = token.interface.parseLog(trc.logs[0]);
  console.log("  event      :", ev.name, ev.args.map(String));
  console.log("  balances   : sender", (await token.balanceOf(sender.address)).toString(), "| receiver", (await token.balanceOf(receiver.address)).toString());

  console.log("\n=== Task 4 demo: failing call (transfer more than balance) ===");
  try { await token.connect(accounts[2]).transfer(sender.address, 9999); }
  catch (e) { console.log("  error:", e.reason || e.shortMessage); }
})().catch(e => { console.error("FAILED:", e.message); process.exit(1); });
