# Lab 2 – Merkle Tree and Tamper Detection

## How to run
Requires only Python 3 (standard library).

```
cd lab2_merkle_tree
python lab2.py
```

Output walks through Tasks 1–4. A saved run is in `lab2.output.txt`.

&nbsp;

## Files and key components

**`lab2.py`**
- `h(s)` – SHA-256 helper used everywhere.
- `build_tree(leaves)` – Task 2. Builds the tree level by level and returns a list of levels (`levels[0]` = leaf hashes, `levels[-1]` = `[root]`). If a level has an odd number of nodes, the last one is duplicated (Bitcoin style).
- `update_leaf(levels, index, new_tx)` – Task 3. Recomputes **only** the hashes on the path from the changed leaf to the root (4 hashes for 8 transactions) and returns how many it computed.
- `proof(levels, index)` / `verify_proof(tx, proof, root)` – builds and checks a Merkle proof: only log2(N) sibling hashes are needed to prove one transaction belongs to the root.
- `__main__` block – hashes 8 transactions, prints the tree, edits one transaction, checks the selective update equals a full rebuild (`assert`), prints the changed node indices per level, and compares the original and new roots.

**`lab2.output.txt`** – saved output.

**Key idea:** one 32-byte root represents all transactions; any change anywhere changes the root.
