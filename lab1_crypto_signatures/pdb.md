# Lab 1 – Cryptographic Primitives and Digital Signatures

## 0. One-time setup (start here if you only copy-pasted the code)

### Prerequisites
| Need | Check with | If missing |
|---|---|---|
| Python 3.9+ | `python --version` (on Mac/Linux use `python3`) | install from python.org; on Windows tick **"Add python.exe to PATH"** |
| pip | `python -m pip --version` | comes with Python |

### Install the dependency
```
cd lab1_crypto_signatures
pip install -r requirements.txt
```
or just `pip install cryptography`. (`hashlib` is built into Python; nothing else is needed.)

Verify: `python -c "import cryptography; print(cryptography.__version__)"`

### Common errors
| Error | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'cryptography'` | `python -m pip install cryptography` (uses the same Python you run) |
| `'python' is not recognized` | reinstall Python with "Add to PATH", or use `py` on Windows / `python3` on Mac/Linux |

&nbsp;

## How to run
Requires Python 3 and the `cryptography` package (`pip install -r requirements.txt`).

```
cd lab1_crypto_signatures
python lab1.py
```

The script prints all four tasks in order: hash, sign, verify, tamper. A saved run is in `lab1.output.txt`.

&nbsp;

## Files and key components

**`lab1.py`**
- `sha256_hex(data)` – Task 1. Hashes a string with SHA-256 and returns the hex digest.
- `sign(private_key, message)` – Task 2. Signs the message with ECDSA (SHA-256 inside) using the private key.
- `verify(public_key, message, signature)` – Task 3 and 4. Returns `True` if the signature matches the message and public key, `False` if `InvalidSignature` is raised.
- `__main__` block – generates a key pair on the **secp256k1** curve (the curve Bitcoin and Ethereum use), signs the transaction, verifies the original, then changes "5 BTC" to "500 BTC" and shows verification fails.

**`lab1.output.txt`** – saved output of a run.

**Why verification fails after tampering:** the signature covers the hash of the message. Any change gives a totally different hash (avalanche effect), so the old signature no longer matches. This gives integrity (changes are detected) and authentication (only the private-key holder could have signed).
