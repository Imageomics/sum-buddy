# sum-buddy
Command-line package to generate a CSV with filepath, filename, and MD5 checksum for all contents of given directory.


## Requirements
Python 3.7+


## Installation

```bash
pip install git+https://github.com/Imageomics/sum-buddy
```


## How it Works

### Command Line Usage

```
usage: sum-buddy [-h] --input-dir INPUT_DIR --output-file OUTPUT_FILE [--ignore-file IGNORE_FILE] [--include-file INCLUDE_FILE]

Generate CSV with filepath, filename, and MD5 checksums for all files in a given directory

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
```

### Python Package Usage
```python
from sumbuddy import get_checksums

input_dir = "path/to/content/dir"
output_file = "./content_checksums.csv"
ignore_file = ".sbignore"   # Optional
include_file = ".sbinclude" # Optional

get_checksums(input_dir, output_file, ignore_file)
# or get_checksums(input_dir, output_file, include_file)
# or get_checksums(input_dir, output_file)

# outputs status bar followed by
# Checksums written to path/to/checksums.csv
```
