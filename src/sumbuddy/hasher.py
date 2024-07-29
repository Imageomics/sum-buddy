import hashlib
from sumbuddy.exceptions import LengthUsedForFixedLengthHashError

class Hasher:
    def __init__(self, algorithm='md5'):
        self.algorithm = algorithm

    def checksum_file(self, file_path, algorithm=None, length=None):
        """
        Calculate the checksum of a file using the specified algorithm.
        
        Parameters:
        ------------
        file_path - String. Path to file to apply checksum function.
        algorithm - String. Hash function to use for checksums. Default: 'md5', see options with 'hashlib.algorithms_available'.
        length - Integer [optional]. Length of the digest for SHAKE and BLAKE algorithms in bytes.
        
        Returns:
        ---------
        String. Hash of file.

        Raises:
        -------
        ValueError - If length is provided for a fixed-length algorithm or unsupported algorithm.
        """
        if algorithm is None:
            algorithm = self.algorithm

        # Validate that selected algorithm is supported
        if algorithm not in hashlib.algorithms_available:
            raise ValueError(f"Unsupported algorithm '{algorithm}'")

        # Define variable length algorithm sets
        shake_algorithms = {'shake_128', 'shake_256'}
        blake_default_lengths = {'blake2s': 32, 'blake2b': 64} 

        # SHAKE algorithm (requires length parameter)
        if algorithm in shake_algorithms:
            if length is None:
                raise ValueError(f"Length parameter [bytes] is required for algorithm '{algorithm}'")
            hash_func = hashlib.new(algorithm)
        
        # BLAKE algorithm (accepts length parameter, but defaults to standard lengths)
        elif algorithm in blake_default_lengths:
            if length:
                hash_func = hashlib.new(algorithm, digest_size=length)
            else:
                default_length = blake_default_lengths[algorithm]
                hash_func = hashlib.new(algorithm)
                print(f"Using default length of {default_length} bytes for {algorithm}")
        
        # Other algorithms
        else:
            if length is not None:
                raise LengthUsedForFixedLengthHashError(algorithm)
            hash_func = hashlib.new(algorithm)

        # Read the file and update the hash function
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)

        # Return the hash digest
        if algorithm in shake_algorithms:
            return hash_func.hexdigest(length)
        else:
            return hash_func.hexdigest()
