#!/usr/bin/env python3
"""Verify a serialized 80-byte Bitcoin mainnet block header."""
import sys, hashlib

MAINNET_POW_LIMIT = 0x00000000FFFF0000000000000000000000000000000000000000000000000000

def decode_compact(bits):
    exponent = bits >> 24
    mantissa = bits & 0x007fffff
    negative = bool(bits & 0x00800000)
    if negative or mantissa == 0:
        raise ValueError("negative or zero compact target")
    if exponent <= 3:
        target = mantissa >> (8 * (3 - exponent))
    else:
        target = mantissa << (8 * (exponent - 3))
    if target <= 0 or target.bit_length() > 256:
        raise ValueError("compact target overflow")
    return target

def verify_header(raw):
    if len(raw) != 80:
        raise ValueError(f"header must be exactly 80 bytes, got {len(raw)}")
    bits = int.from_bytes(raw[72:76], "little")
    target = decode_compact(bits)
    if target > MAINNET_POW_LIMIT:
        raise ValueError("target exceeds Bitcoin mainnet proof-of-work limit")
    digest = hashlib.sha256(hashlib.sha256(raw).digest()).digest()
    actual = int.from_bytes(digest, "little")
    return {
        "valid_pow": actual <= target,
        "hash": digest[::-1].hex(),
        "target": f"{target:064x}",
        "bits": f"{bits:08x}",
        "nonce": int.from_bytes(raw[76:80], "little"),
        "hash_value": f"{actual:064x}",
    }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_bitcoin_header.py <80-byte-header-hex>")
    try:
        result = verify_header(bytes.fromhex(sys.argv[1]))
    except (ValueError, TypeError) as exc:
        raise SystemExit(f"INVALID HEADER: {exc}")
    for key, value in result.items():
        print(f"{key}={value}")
    raise SystemExit(0 if result["valid_pow"] else 1)
