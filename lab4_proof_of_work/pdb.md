# Lab 4 – Proof-of-Work, Nonce and Mining Difficulty

## How to run
Requires only Python 3 (standard library). Difficulty 6 takes a few seconds.

```
cd lab4_proof_of_work
python lab4.py
```

A saved run is in `lab4.output.txt`. Results vary run to run only if you change the data; the nonce for given data is deterministic.

&nbsp;

## Files and key components

**`lab4.py`**
- `mine(block_data, prev_hash, difficulty)` – Tasks 1–3. Tries nonce 0, 1, 2… hashing `prev_hash + data + nonce` until the hash starts with `difficulty` zeros. Returns nonce, hash, attempts and time.
- `mine_target(block_data, prev_hash, target)` – Task 4. Same search but the condition is `int(hash) < target`, which is how real chains express difficulty.
- `__main__` block – mines at difficulty 4, then loops difficulty 1–6 to compare attempts and time, then shows targets for difficulty 3, 4, 5 (`target = 2^(256 − 4·d)`).

**To change difficulty as an examiner asks:** edit the `4` in the first `mine(...)` call or the `range(1, 7)` loop.

**Key idea:** each extra leading hex zero makes the target 16× smaller, so expected work grows about 16× per step. Lower target means higher difficulty and more mining effort.

**`lab4.output.txt`** – saved output.
