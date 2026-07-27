from sumbuddy.__about__ import __version__
from sumbuddy.__main__ import get_checksums
from sumbuddy.hasher import Hasher
from sumbuddy.mapper import Mapper

# Create instances of the classes
mapper_instance = Mapper()
hasher_instance = Hasher()

# Expose the instance methods
gather_file_paths = mapper_instance.gather_file_paths
checksum_file = hasher_instance.checksum_file

__all__ = ["__version__", "checksum_file", "gather_file_paths", "get_checksums"]
