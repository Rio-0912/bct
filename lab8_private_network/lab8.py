"""Lab 8 - Private Ethereum network (3 geth nodes, Clique PoA) driven through Docker.

Run:  python lab8.py          (set up + run all tasks)
      python lab8.py cleanup  (remove containers, volumes, network)
"""
import json
import subprocess
import sys
import time

IMG = "ethereum/client-go:v1.13.15"
NET = "lab8net"
SUBNET = "172.30.0.0/24"
NODES = {1: "172.30.0.11", 2: "172.30.0.12", 3: "172.30.0.13"}
PW = "labpass"
CHAIN_ID = 1337


def sh(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True, shell=isinstance(cmd, str))
    if check and r.returncode != 0:
        raise RuntimeError(f"{cmd}\n{r.stdout}\n{r.stderr}")
    return r.stdout.strip()


def cleanup():
    for i in NODES:
        sh(["docker", "rm", "-f", f"lab8-node{i}"], check=False)
        sh(["docker", "volume", "rm", "-f", f"lab8-data{i}"], check=False)
    sh(["docker", "network", "rm", NET], check=False)


def run_helper(vol, script):
    return sh(["docker", "run", "--rm", "--entrypoint", "sh", "-v", f"{vol}:/root/.ethereum", IMG, "-c", script])


def js(i, expr):
    """Evaluate a JS expression in node i's geth console."""
    return sh(["docker", "exec", f"lab8-node{i}", "geth", "attach", "--exec", expr, "/root/.ethereum/geth.ipc"])


def banner(t):
    print(f"\n{'=' * 8} {t} {'=' * 8}")


def setup():
    cleanup()
    sh(["docker", "network", "create", "--subnet", SUBNET, NET])
    addrs = {}
    for i in NODES:
        sh(["docker", "volume", "create", f"lab8-data{i}"])
        run_helper(f"lab8-data{i}", f"echo {PW} > /root/.ethereum/pw.txt")
        out = run_helper(f"lab8-data{i}", "geth account new --datadir /root/.ethereum --password /root/.ethereum/pw.txt")
        addrs[i] = [l.split()[-1] for l in out.splitlines() if "Public address" in l][0].lower()
    extradata = "0x" + "00" * 32 + "".join(a[2:] for a in addrs.values()) + "00" * 65
    genesis = {
        "config": {"chainId": CHAIN_ID, "homesteadBlock": 0, "eip150Block": 0, "eip155Block": 0, "eip158Block": 0,
                   "byzantiumBlock": 0, "constantinopleBlock": 0, "petersburgBlock": 0, "istanbulBlock": 0,
                   "berlinBlock": 0, "londonBlock": 0, "clique": {"period": 2, "epoch": 30000}},
        "difficulty": "1", "gasLimit": "8000000", "extradata": extradata,
        "alloc": {addrs[1]: {"balance": "1000000000000000000000"}, addrs[2]: {"balance": "1000000000000000000000"}},
    }
    g = json.dumps(genesis).replace('"', '\\"')
    for i in NODES:
        run_helper(f"lab8-data{i}", f'echo "{g}" > /root/.ethereum/genesis.json && geth init --datadir /root/.ethereum /root/.ethereum/genesis.json')
    for i, ip in NODES.items():
        sh(["docker", "run", "-d", "--name", f"lab8-node{i}", "--network", NET, "--ip", ip,
            "-v", f"lab8-data{i}:/root/.ethereum", IMG,
            "--datadir", "/root/.ethereum", "--networkid", str(CHAIN_ID), "--port", "30303",
            "--nat", f"extip:{ip}", "--nodiscover", "--syncmode", "full",
            "--http", "--http.addr", "0.0.0.0", "--http.api", "eth,net,web3,admin,clique,txpool",
            "--http.vhosts", "*", "--unlock", addrs[i], "--password", "/root/.ethereum/pw.txt",
            "--allow-insecure-unlock", "--mine", "--miner.etherbase", addrs[i]])
    time.sleep(6)
    return addrs


def enode(i):
    e = js(i, "admin.nodeInfo.enode").strip('"')
    return e.split("@")[0] + f"@{NODES[i]}:30303"


def connect_all():
    for i in (2, 3):
        js(i, f'admin.addPeer("{enode(1)}")')
    js(2, f'admin.addPeer("{enode(3)}")')
    time.sleep(4)


def main():
    banner("TASK 1: start 3 preinitialised nodes (same genesis, Clique PoA, chainId 1337)")
    addrs = setup()
    print(sh(["docker", "ps", "--filter", "name=lab8-node", "--format", "{{.Names}}  {{.Status}}  {{.Networks}}"]))
    for i in NODES:
        print(f"node{i}: ip={NODES[i]} signer/account={addrs[i]}")
    connect_all()

    banner("TASK 2: same network & peer connectivity")
    for i in NODES:
        print(f"node{i}: peerCount={js(i, 'net.peerCount')}  genesisHash={js(i, 'eth.getBlock(0).hash')}  "
              f"networkId={js(i, 'admin.nodeInfo.protocols.eth.network')}  block={js(i, 'eth.blockNumber')}")
    print("node1 peers:", js(1, "admin.peers.map(function(p){return p.network.remoteAddress})"))
    print("clique signers:", js(1, "clique.getSigners()"))

    banner("TASK 3: transaction from node1's account, observed from node3")
    h = js(1, f'eth.sendTransaction({{from: "{addrs[1]}", to: "{addrs[3]}", value: web3.toWei(5, "ether")}})')
    print("tx hash submitted on node1:", h)
    time.sleep(6)
    print("node3 sees tx   :", js(3, f"eth.getTransaction({h}).blockNumber"), "(blockNumber)")
    print("node3 receipt   :", js(3, f"JSON.stringify({{status: eth.getTransactionReceipt({h}).status, block: eth.getTransactionReceipt({h}).blockNumber, gas: eth.getTransactionReceipt({h}).gasUsed}})"))
    print("node3 balance of recipient (ETH):", js(3, f'web3.fromWei(eth.getBalance("{addrs[3]}"), "ether")'))
    n = js(1, "eth.blockNumber")
    print(f"block {n}  node1={js(1, f'eth.getBlock({n}).hash')}\n          node3={js(3, f'eth.getBlock({n}).hash')}")

    banner("TASK 4: fault injection - stop node3, observe, restore")
    sh(["docker", "stop", "lab8-node3"])
    time.sleep(4)
    print("node3 stopped. node1 peerCount =", js(1, "net.peerCount"), "(was 2)")
    b1 = js(1, "eth.blockNumber")
    js(1, f'eth.sendTransaction({{from: "{addrs[1]}", to: "{addrs[2]}", value: web3.toWei(1, "ether")}})')
    time.sleep(8)
    print(f"chain continues with 2 of 3 signers (Clique needs >50%): block {b1} -> {js(1, 'eth.blockNumber')}")
    sh(["docker", "start", "lab8-node3"])
    time.sleep(6)
    print("node3 restarted; its peers (before re-adding):", js(3, "net.peerCount"))
    js(3, f'admin.addPeer("{enode(1)}")')
    js(3, f'admin.addPeer("{enode(2)}")')
    time.sleep(8)
    print("after addPeer: node3 peerCount =", js(3, "net.peerCount"),
          "| node3 block =", js(3, "eth.blockNumber"), "| node1 block =", js(1, "eth.blockNumber"))
    print("""
Explanation: with --nodiscover, peers are not found automatically, so after a restart
a node only has the connections that other nodes re-dial to it; the rest must be
re-added with admin.addPeer (or listed in static-nodes.json).
Clique PoA keeps producing blocks while a majority (2 of 3) of signers is online;
the returning node syncs missing blocks from its peers and catches up to the head.
A configuration mismatch (e.g. different --networkid or genesis) would make the
handshake fail and peerCount would stay 0.""")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        cleanup()
        print("cleaned up")
    else:
        main()
