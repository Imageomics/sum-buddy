from sumbuddy.__main__ import get_checksums
from sumbuddy.mapper import Mapper
from sumbuddy.hasher import Hasher

# Create instances of the classes
mapper_instance = Mapper()
hasher_instance = Hasher()

# Expose the instance methods
gather_file_paths = mapper_instance.gather_file_paths
checksum = hasher_instance.checksum

__all__ = ["checksum", "get_checksums", "gather_file_paths"]
