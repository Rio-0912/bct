"""Lab 1 - SHA-256 hashing + ECDSA (secp256k1) digital signatures."""
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def sign(private_key, message: str) -> bytes:
    return private_key.sign(message.encode(), ec.ECDSA(hashes.SHA256()))


def verify(public_key, message: str, signature: bytes) -> bool:
    try:
        public_key.verify(signature, message.encode(), ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False


if __name__ == "__main__":
    tx = "Alice pays Bob 5 BTC | nonce=42"
    print("=== Task 1: SHA-256 ===")
    print("Message :", tx)
    print("Digest  :", sha256_hex(tx))

    print("\n=== Task 2: Generate keys and sign ===")
    priv = ec.generate_private_key(ec.SECP256K1())  # same curve as Bitcoin/Ethereum
    pub = priv.public_key()
    print("Public key (PEM):\n" + pub.public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode())
    sig = sign(priv, tx)
    print("Signature (hex):", sig.hex())

    print("\n=== Task 3: Verify original ===")
    print("Verification result:", verify(pub, tx, sig))

    print("\n=== Task 4: Tamper with message ===")
    tampered = "Alice pays Bob 500 BTC | nonce=42"
    print("Tampered message   :", tampered)
    print("Tampered SHA-256   :", sha256_hex(tampered))
    print("Verification result:", verify(pub, tampered, sig))
    print("""
Explanation: a signature is computed over the hash of the message. Changing even
one character gives a completely different SHA-256 digest (avalanche effect), so
the signature no longer matches -> verification fails. This gives:
 - Integrity: any modification of a transaction is detected.
 - Authentication / non-repudiation: only the holder of the private key could
   produce a valid signature, verifiable by anyone with the public key.
Blockchains rely on this so nobody can alter or forge transactions.""")
