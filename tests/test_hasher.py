import hashlib
import os
import tempfile
import unittest
from sumbuddy.hasher import Hasher

class TestHasher(unittest.TestCase):
    """
    Correct answers generated with (where items in [square brackets] are optional depending on the algorithm): 
    with open('test_file.txt', "wb") as f:
        file.write(b'This is a test file.')
    hash_func = hashlib.new('<algorithm>', [digest_size=<length>])
    with open('test_file.txt', "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    hash_func.hexdigest([<length>])
    """
    checksums = {
        "md5": "3de8f8b0dc94b8c2230fab9ec0ba0506",
        "sha1": "26d82f1931cbdbd83c2a6871b2cecd5cbcc8c26b",
        "sha224": "47bc9874c3715f9f4b6b63d10b87803e2adb564ae88f3912975542c8",
        "sha256": "f29bc64a9d3732b4b9035125fdb3285f5b6455778edca72414671e0ca3b2e0de",
        "sha384": "ae5dd957590ab86fd7359f43ecb68b8734d501271ca2d3953b7209ed63a98dfb86cf66e2c5848cc2471abdd80578670a",
        "sha512": "b1df216b5b05e3965c469492744a5de0c945e0b103c42eb1e57476fbed8f1d489f5cae9b792db37c5d823bc0c6c7d06b056176d6abe5ce076eeadaed414e17a3",
        "blake2b": "d7d25714b54ae8e63105f3a445ae2ac575b1540dc6070e1228d5eba0f461f8e27af66716dc8d73d7f85f7c55a17c2e97ec8ab6caaef3e98380605044a1e53575",
        "blake2s": "68dfdbcbbaa3b8447adeb0634e1329ce74142bd673589ed7f3e6db910132a15d",
        "sha3_224": "02f482b6fc8462a98f65224e81eb5425bd2157a02e7e64912fb39df1",
        "sha3_256": "aa49cf654dc0b2a9ee97890fb81c6d898c5c03f441baaf2f1c9adffe00d3e561",
        "sha3_384": "1c635201d12b87839b626b26c57b81216d616c984dc42d5afa17a905402267817ac787abfc24072e18e77f921eb6a23f",
        "sha3_512": "a872d9efeb2a31fe92cf116e5ca8c9b57b07b200c91adc0a26ff58f32b5c2f5bd69671809e8a85383da8e51e6f64cc74af4470832bbbe17cde35391d4fb0fbe8",
        "shake_128": "d387bbb179a29a607bb86d119dfdab2f5961c254cedb7cbd9a8157c290d48812",
        "shake_256": "db0b571b3252be360bf6d720f75bce209a75cdf4184db200cc9c72028b14e23a4527bf7d491e8fcf998a1bee474c2824930f8f9ab0ef4062120313f81a9e6774",
        "ripemd160": "8ee2970b47aa341b39699bf52cce3e43a9b5e11c",
        "sha512_256": "abe5f1fd1934c5c91ff5ba1912362402ee6c0cb79814898feee8dc07ffe85f95",
        "sm3": "98226efe610707b79497cf6c08c270b6c2a7c60b5ab40cd3483da9cd3668b5f2",
        "sha512_224": "a1af41114c501d2c30c1fe259d794e672dc66ae86b0e77173ae714fd",
        "md5-sha1": "3de8f8b0dc94b8c2230fab9ec0ba050626d82f1931cbdbd83c2a6871b2cecd5cbcc8c26b"
    }

    def setUp(self):
        self.hasher = Hasher()
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b'This is a test file.')
        self.temp_file_path = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        os.remove(self.temp_file_path)

    def test_checksum_file(self):
        self._test_checksum_file_with_algorithm()

    def test_checksum_file_md5(self):
        self._test_checksum_file_with_algorithm("md5")

    def test_checksum_file_sha1(self):
        self._test_checksum_file_with_algorithm("sha1")

    def test_checksum_file_sha224(self):
        self._test_checksum_file_with_algorithm("sha224")

    def test_checksum_file_sha256(self):
        self._test_checksum_file_with_algorithm("sha256")

    def test_checksum_file_sha384(self):
        self._test_checksum_file_with_algorithm("sha384")

    def test_checksum_file_sha512(self):
        self._test_checksum_file_with_algorithm("sha512")

    def test_checksum_file_blake2b(self):
        self._test_checksum_file_with_algorithm("blake2b")

    def test_checksum_file_blake2s(self):
        self._test_checksum_file_with_algorithm("blake2s")

    def test_checksum_file_sha3_224(self):
        self._test_checksum_file_with_algorithm("sha3_224")

    def test_checksum_file_sha3_256(self):
        self._test_checksum_file_with_algorithm("sha3_256")

    def test_checksum_file_sha3_384(self):
        self._test_checksum_file_with_algorithm("sha3_384")

    def test_checksum_file_sha3_512(self):
        self._test_checksum_file_with_algorithm("sha3_512")

    def test_checksum_file_shake_128(self):
        self._test_checksum_file_with_algorithm("shake_128", length=32) 

    def test_checksum_file_shake_256(self):
        self._test_checksum_file_with_algorithm("shake_256", length=64) 
    
    def test_checksum_fileripemd160(self):
        self._test_checksum_file_with_algorithm("ripemd160")

    def test_checksum_file_sha512_256(self):
        self._test_checksum_file_with_algorithm("sha512_256")

    def test_checksum_file_sm3(self):
        self._test_checksum_file_with_algorithm("sm3")

    def test_checksum_file_sha512_224(self):
        self._test_checksum_file_with_algorithm("sha512_224")

    def test_checksum_file_md5_sha1(self):
        self._test_checksum_file_with_algorithm("md5-sha1")
        

    def _test_checksum_file_with_algorithm(self, algorithm="md5", length=None):
        expected_checksum = self.checksums[algorithm]
        if length:
            checksum = self.hasher.checksum_file(self.temp_file_path, algorithm=algorithm, length=length)
        else:
            checksum = self.hasher.checksum_file(self.temp_file_path, algorithm=algorithm)
        self.assertEqual(checksum, expected_checksum)

    def test_algorithms_coverage(self):
        algorithms_available = hashlib.algorithms_available
        algorithms_covered = set(self.checksums.keys())
        
        self.assertEqual(algorithms_covered, algorithms_available, 
                        "The algorithms in checksums do not exactly match the available algorithms in hashlib")

if __name__ == '__main__':
    unittest.main()
