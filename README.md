# sum-buddy
Command-line package to generate a CSV with filepath, filename, and checksum for all contents of given directory.


## Requirements
Python 3.7+


## Installation

```bash
pip install git+https://github.com/Imageomics/sum-buddy
```


## How it Works

### Command Line Usage

```
usage: sum-buddy [-h] --input-dir INPUT_DIR --output-file OUTPUT_FILE [--ignore-file IGNORE_FILE] [--include-file INCLUDE_FILE] [--algorithm ALGORITHM]

Generate CSV with filepath, filename, and checksums for all files in a given directory

options:
  -h, --help            show this help message and exit
  --input-dir INPUT_DIR
                        Directory to traverse for files
  --output-file OUTPUT_FILE
                        Filepath for the output CSV file
  --ignore-file IGNORE_FILE
                        Filepath for the ignore patterns file
  --include-file INCLUDE_FILE
                        Filepath for the include patterns file
  --algorithm ALGORITHM
                        Hash algorithm to use (default: md5, see options with 'hashlib.algorithms_available')
```

### Python Package Usage
```python
from sumbuddy import get_checksums, gather_file_paths, checksum

input_dir = "path/to/content/dir"
output_file = "path/to/checksums.csv"
ignore_file = ".sbignore"   # Optional
include_file = ".sbinclude" # Optional
algorighm = "md5"           # Optional, possible inputs include list elements returned by hashlib.algorithms_available

# To generate checksums and save to a CSV file
get_checksums(input_dir, output_file, ignore_file, algorithm)
# or get_checksums(input_dir, output_file, include_file)
# or get_checksums(input_dir, output_file)

# outputs status bar followed by
# Checksums written to path/to/checksums.csv

# To gather a list of file paths according to ignore/include patterns
file_paths = gather_file_paths(input_dir, ignore_file=ignore_file)
# or file_paths = gather_file_paths(input_dir, include_file=include_file)
# or file_paths = gather_file_paths(input_dir)

# To calculate the checksum of a single file
checksum = checksum("path/to/file")
