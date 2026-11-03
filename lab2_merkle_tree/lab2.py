"""Lab 2 - Merkle tree, root, selective path recomputation, tamper detection."""
import hashlib


def h(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def build_tree(leaves):
    """Return list of levels; levels[0]=leaf hashes, levels[-1]=[root]."""
    level = list(leaves)
    levels = [level]
    while len(level) > 1:
        if len(level) % 2:  # odd count -> duplicate last (Bitcoin style)
            level = level + [level[-1]]
            levels[-1] = level
        level = [h(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
        levels.append(level)
    return levels


def update_leaf(levels, index, new_tx):
    """Recompute ONLY the hashes on the path from leaf to root. Returns #hashes computed."""
    count = 0
    levels[0][index] = h(new_tx)
    count += 1
    for d in range(len(levels) - 1):
        lvl = levels[d]
        pair = index - (index % 2)
        left = lvl[pair]
        right = lvl[pair + 1] if pair + 1 < len(lvl) else lvl[pair]
        index //= 2
        levels[d + 1][index] = h(left + right)
        count += 1
    return count


def proof(levels, index):
    p = []
    for d in range(len(levels) - 1):
        lvl = levels[d]
        sib = index ^ 1
        p.append((lvl[sib] if sib < len(lvl) else lvl[index], sib < index))
        index //= 2
    return p


def verify_proof(tx, p, root):
    cur = h(tx)
    for sib, sib_is_left in p:
        cur = h(sib + cur) if sib_is_left else h(cur + sib)
    return cur == root


if __name__ == "__main__":
    txs = ["Alice->Bob:10", "Bob->Carol:4", "Carol->Dave:2", "Dave->Eve:7",
           "Eve->Frank:1", "Frank->Gina:3", "Gina->Hal:9", "Hal->Ivy:6"]
    print("Task 1: transaction hashes ")
    leaves = [h(t) for t in txs]
    for t, x in zip(txs, leaves):
        print(f"{t:<16} {x}")

    print("\n=== Task 2: Merkle tree ===")
    levels = build_tree(leaves)
    for i, l in enumerate(levels):
        print(f"Level {i} ({len(l)} nodes)")
        for x in l:
            print("   ", x[:16] + "...")
    orig_root = levels[-1][0]
    print("Merkle root:", orig_root)

    print("\n=== Task 3: modify tx at index 2, recompute only the path ===")
    old_levels = [list(l) for l in levels]
    txs[2] = "Carol->Dave:2000"
    n = update_leaf(levels, 2, txs[2])
    print(f"Hashes recomputed: {n} (vs {sum(len(l) for l in levels)} nodes for a full rebuild)")
    new_root = levels[-1][0]
    assert new_root == build_tree([h(t) for t in txs])[-1][0], "selective != full rebuild"
    print("Selective recomputation matches full rebuild: True")
    for d, (a, b) in enumerate(zip(old_levels, levels)):
        changed = [i for i in range(len(a)) if a[i] != b[i]]
        print(f"  level {d}: changed node indices {changed}")

    print("\n=== Task 4: compare roots ===")
    print("Original root:", orig_root)
    print("Modified root:", new_root)
    print("Roots equal  :", orig_root == new_root)
    p = proof(levels, 2)
    print("Merkle proof for modified tx verifies against new root :", verify_proof(txs[2], p, new_root))
    print("Same proof with ORIGINAL tx against new root           :", verify_proof("Carol->Dave:2", p, new_root))
    print("""
Explanation: any change to a transaction changes its leaf hash and every hash on
its path to the root, so the root changes. Comparing a single 32-byte root
detects tampering in any of the N transactions. To prove one transaction is in a
block you need only log2(N) sibling hashes (here 3 of 8 leaves), and updating one
transaction needs only log2(N)+1 hashes instead of rehashing everything.""")
