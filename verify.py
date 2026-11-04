#!/usr/bin/env python3
"""Independent check: does nonce solve prefix at N bits? Exit 0 = valid."""
import hashlib, struct, sys

def lz_bits(h: bytes) -> int:
    n = 0
    for b in h:
        if b == 0:
            n += 8
            continue
        return n + (8 - b.bit_length())
    return n

prefix_hex, nonce, n_bits = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
hdr = bytes.fromhex(prefix_hex) + struct.pack("<I", nonce)
h = hashlib.sha256(hashlib.sha256(hdr).digest()).digest()
ok = lz_bits(h) >= n_bits
print(f"{'VALID' if ok else 'INVALID'} lz={lz_bits(h)} need={n_bits} hash={h.hex()}")
sys.exit(0 if ok else 1)
