import hashlib

class Hasher:
    def __init__(self, algorithm='md5'):
        self.algorithm = algorithm

    def checksum(self, file_path, algorithm=None):
        """
        Calculate the checksum of a file using the specified algorithm.
        
        Parameters:
        ------------
        file_path - String. Path to file to apply checksum function.
        algorithm - String. Hash function to use for checksums. Default: 'md5', see options with 'hashlib.algorithms_available'.
        
        Returns:
        ---------
        hashlib.<algorithm>.hexdigest - String. Hash of file.
        """
        if algorithm is None:
            algorithm = self.algorithm
        hash_func = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
