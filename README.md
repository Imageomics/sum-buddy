# sum-buddy
Command-line package to generate a CSV with filepath, filename, and MD5 checksum for all contents of given directory.


## Requirements
Python 3.7+


## Installation

```bash
pip install git+https://github.com/Imageomics/sum-buddy
```


## How it Works

```
usage: sum-buddy [-h] --input-dir INPUT_DIR --output-file OUTPUT_FILE

Generate CSV with filepath, filename, and MD5 checksums for all files in a given directory

options:
  -h, --help            show this help message and exit
  --input-dir INPUT_DIR
                        Directory to traverse for files
  --output-file OUTPUT_FILE
                        Filepath for the output CSV file
```
