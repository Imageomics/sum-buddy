import hashlib

class Hasher:
    def __init__(self, algorithm='md5'):
        self.algorithm = algorithm

    def checksum(self, file_path, algorithm=None):
        """
        Calculate the checksum of a file using the specified algorithm.
        """
        if algorithm is None:
            algorithm = self.algorithm
        hash_func = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    def md5_checksum(self, file_path):
        """
        Calculate the MD5 checksum of a file.
        """
        return self.checksum(file_path, 'md5')
