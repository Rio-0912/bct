"""Lab 4 - Proof of Work, nonce, difficulty."""
import hashlib
import time


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def mine(block_data: str, prev_hash: str, difficulty: int):
    """Difficulty = number of leading hex zeros. Returns (nonce, hash, attempts, seconds)."""
    prefix = "0" * difficulty
    nonce, start = 0, time.perf_counter()
    while True:
        digest = sha(f"{prev_hash}{block_data}{nonce}")
        if digest.startswith(prefix):
            return nonce, digest, nonce + 1, time.perf_counter() - start
        nonce += 1


def mine_target(block_data, prev_hash, target: int):
    """Target-based form: hash (as integer) must be < target."""
    nonce = 0
    while int(sha(f"{prev_hash}{block_data}{nonce}"), 16) >= target:
        nonce += 1
    return nonce, sha(f"{prev_hash}{block_data}{nonce}"), nonce + 1


if __name__ == "__main__":
    data, prev = "Alice pays Bob 10", "0" * 64
    print("=== Tasks 1-2: mine at difficulty 4 ===")
    nonce, digest, attempts, secs = mine(data, prev, 4)
    print(f"nonce={nonce}\nhash ={digest}\nattempts={attempts}  time={secs:.4f}s")

    print("\n=== Task 3: compare difficulties 1..6 ===")
    print(f"{'diff':>4} {'nonce':>10} {'attempts':>10} {'time(s)':>9}  hash")
    for d in range(1, 7):
        n, hx, a, t = mine(data, prev, d)
        print(f"{d:>4} {n:>10} {a:>10} {t:>9.4f}  {hx[:24]}...")

    print("\n=== Task 4: target view ===")
    for d in (3, 4, 5):
        target = 1 << (256 - 4 * d)  # d leading hex zeros == 4d leading zero bits
        n, hx, a = mine_target(data, prev, target)
        print(f"difficulty {d}: target=2^{256 - 4 * d}  nonce={n}  attempts={a}  hash={hx[:20]}...")
    print("""
Explanation: a valid block hash must be numerically below the target. Each extra
leading hex zero shrinks the target 16x, so the success probability per attempt
is 1/16^d and the expected work is 16^d hashes (~16x per +1 difficulty). Lower
target = higher difficulty = more mining effort. Bitcoin retargets difficulty
every 2016 blocks to keep ~10 min block time. Results vary by luck (nonce search
is random), but average effort grows exponentially.""")
