// Lab 5: compile (npx hardhat compile), deploy, state change, query, receipt, modify rule.
const hre = require("hardhat");
const { ethers } = hre;

async function main() {
  const [owner, user] = await ethers.getSigners();

  console.log("=== Task 1: Deploy SimpleBank ===");
  const Bank = await ethers.getContractFactory("SimpleBank");
  const bank = await Bank.deploy();
  const dtx = bank.deploymentTransaction();
  await bank.waitForDeployment();
  const drc = await dtx.wait();
  console.log("Address:", await bank.getAddress(), "| deployed in block", drc.blockNumber, "| gas", drc.gasUsed.toString());

  console.log("\n=== Task 2: state change (deposit 1 ETH) + read ===");
  const tx = await bank.connect(user).deposit({ value: ethers.parseEther("1") });
  const rc = await tx.wait();
  console.log("balances[user] =", ethers.formatEther(await bank.getBalance(user.address)), "ETH");

  console.log("\n=== Task 3: transaction details ===");
  console.log("tx hash :", rc.hash);
  console.log("status  :", rc.status === 1 ? "SUCCESS" : "FAILED");
  console.log("block   :", rc.blockNumber);
  console.log("gas used:", rc.gasUsed.toString());
  console.log("events  :", rc.logs.map(l => bank.interface.parseLog(l).name + " " + bank.interface.parseLog(l).args.map(String)));
  console.log("contract ETH balance:", ethers.formatEther(await ethers.provider.getBalance(await bank.getAddress())));

  console.log("\n=== Task 4: modify rule - owner raises minDeposit to 2 ETH ===");
  console.log("Before: 0.5 ETH deposit allowed? ->", await tryDeposit(bank, user, "0.5"));
  await (await bank.connect(owner).setMinDeposit(ethers.parseEther("2"))).wait();
  console.log("minDeposit now:", ethers.formatEther(await bank.minDeposit()), "ETH");
  console.log("After : 0.5 ETH deposit allowed? ->", await tryDeposit(bank, user, "0.5"));
  console.log("After : 2.5 ETH deposit allowed? ->", await tryDeposit(bank, user, "2.5"));
  try { await bank.connect(user).setMinDeposit(0); console.log("non-owner changed rule (BAD)"); }
  catch (e) { console.log("non-owner setMinDeposit reverted ->", e.message.match(/Only owner/) ? "Only owner" : e.message); }
}
async function tryDeposit(bank, s, eth) {
  try { await (await bank.connect(s).deposit({ value: ethers.parseEther(eth) })).wait(); return "yes"; }
  catch (e) { return "NO (" + (e.message.match(/Deposit below minimum/) || ["reverted"])[0] + ")"; }
}
main().catch(e => { console.error(e); process.exit(1); });
