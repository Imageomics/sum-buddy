import hashlib
import os
import tempfile
import pytest
from unittest.mock import patch
from sumbuddy.hasher import Hasher
from sumbuddy.exceptions import LengthUsedForFixedLengthHashError

def is_algorithm_available(algorithm):
    return algorithm in hashlib.algorithms_available

def is_algorithm_guaranteed(algorithm):
    return algorithm in hashlib.algorithms_guaranteed

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

shake_algorithms = {'shake_128', 'shake_256'}
blake_algorithms_with_defaults = {'blake2s': 32, 'blake2b': 64}

@pytest.fixture(scope="module")
def temp_file():
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(b'This is a test file.')
    temp_file_path = temp_file.name
    temp_file.close()
    yield temp_file_path
    os.remove(temp_file_path)

@pytest.mark.parametrize("algorithm", checksums.keys())
def test_all_algorithms_with_defaults(temp_file, algorithm):
    if not is_algorithm_available(algorithm):
        if is_algorithm_guaranteed(algorithm):
            pytest.fail(f"{algorithm} is guaranteed but not available.")
        pytest.skip(f"{algorithm} not available on system and not guaranteed.")

    if algorithm == "shake_128":
        length = 32
    elif algorithm == "shake_256":
        length = 64
    elif algorithm in blake_algorithms_with_defaults:
        length = blake_algorithms_with_defaults[algorithm]
    else:
        length = None

    hasher = Hasher()
    if length:
        checksum = hasher.checksum_file(temp_file, algorithm=algorithm, length=length)
    else:
        checksum = hasher.checksum_file(temp_file, algorithm=algorithm)
    assert checksum == checksums[algorithm], f"Assertion failed for {algorithm} with length {length}"

    if algorithm in blake_algorithms_with_defaults:
        length = None
        checksum = hasher.checksum_file(temp_file, algorithm=algorithm)
        assert checksum == checksums[algorithm], f"Assertion failed for {algorithm} with length {length}"

@patch('hashlib.algorithms_available', new_callable=lambda: hashlib.algorithms_guaranteed)
@pytest.mark.parametrize("algorithm", checksums.keys())
def test_only_guaranteed_algorithms_available(mock_algorithms, temp_file, algorithm):
    '''
    Run algorithm tests as if those that are not guaranteed are unavailable in the system.
    Skips are expected, but each algorithm should only be skipped once unless it is actually unavailable on the system running the testing.
    '''
    test_all_algorithms_with_defaults(temp_file, algorithm)

def test_invalid_length_for_fixed_length_algorithm(temp_file):
    hasher = Hasher()
    with pytest.raises(LengthUsedForFixedLengthHashError):
        hasher.checksum_file(temp_file, algorithm="md5", length=10)

def test_nonexistent_file():
    hasher = Hasher()
    with pytest.raises(FileNotFoundError):
        hasher.checksum_file("non_existent_file.txt", algorithm="md5")

def test_algorithms_available_coverage():
    algorithms_available = hashlib.algorithms_available
    algorithms_covered = set(checksums.keys())
    
    missing_algorithms = algorithms_available - algorithms_covered

    print(f"Available algorithms to hashlib: {algorithms_available}")
    print(f"Covered algorithms: {algorithms_covered}")
    print(f"Avalable algs to hashlib not covered: {missing_algorithms}")
    print(f"Covered algs not available to hashlib: {algorithms_covered - algorithms_available} (skipped in tests)")

    assert not missing_algorithms, f"The following algorithms are available to hashlib but not covered in tests: {missing_algorithms}"

def test_guaranteed_algorithm_coverage():
    algorithms_guaranteed = hashlib.algorithms_guaranteed
    algorithms_covered = set(checksums.keys())

    missing_algorithms = algorithms_guaranteed - algorithms_covered

    assert not missing_algorithms, f"The following guaranteed algorithms are not covered in tests: {missing_algorithms}"
