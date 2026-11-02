# Lab 3 – Simple Blockchain using Python

## How to run
Requires only Python 3 (standard library).

```
cd lab3_simple_blockchain
python lab3.py
```

A saved run is in `lab3.output.txt`.

&nbsp;

## Files and key components

**`lab3.py`**
- `Block` class – holds `index`, `timestamp`, `data`, `previous_hash` and `hash`. `compute_hash()` SHA-256-hashes all the other fields as sorted JSON, so changing any field changes the hash.
- `Blockchain` class
  - `__init__` – creates the genesis block (previous hash = 64 zeros).
  - `add_block(data)` – new block stores the previous block's hash (the linkage).
  - `validate()` – for each block checks (1) the stored hash equals a recomputed hash, and (2) `previous_hash` equals the prior block's hash.
- `__main__` block – builds a chain of 3 blocks plus genesis, validates it (valid), then tampers three ways:
  1. Edit block 1's data → caught: content doesn't match stored hash.
  2. Also recompute block 1's hash → caught: block 2's `previous_hash` no longer matches.
  3. Recompute every later block too → passes locally; in a real network this is stopped by proof-of-work and consensus (Lab 4).

**`lab3.output.txt`** – saved output.
