import unittest
from verify_bitcoin_header import verify_header

GENESIS = bytes.fromhex(
    "01000000" + "00"*32 +
    "3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a" +
    "29ab5f49" + "ffff001d" + "1dac2b7c"
)

class BitcoinHeaderTests(unittest.TestCase):
    def test_genesis_header_pow(self):
        result = verify_header(GENESIS)
        self.assertTrue(result["valid_pow"])
        self.assertEqual(result["hash"],
            "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f")
        self.assertEqual(result["nonce"], 2083236893)

    def test_mutated_header_fails_pow(self):
        mutated = bytearray(GENESIS)
        mutated[4] ^= 1
        self.assertFalse(verify_header(bytes(mutated))["valid_pow"])

    def test_rejects_wrong_length(self):
        with self.assertRaises(ValueError):
            verify_header(GENESIS[:-1])

    def test_rejects_negative_compact_target(self):
        mutated = bytearray(GENESIS)
        mutated[74] |= 0x80
        with self.assertRaises(ValueError):
            verify_header(bytes(mutated))

if __name__ == "__main__":
    unittest.main()
