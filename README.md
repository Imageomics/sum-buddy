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

#### CLI Examples
You may use the `examples/` directory to test the CLI.

```bash
sum-buddy --input-dir examples/example_content --output-file examples/checksums.csv --ignore-file examples/.sbignore_all --algorithm md5
Calculating checksums: 0it [00:00, ?it/s]
Checksums written to examples/checksums.csv
cat examples/checksums.csv 
filepath,filename,md5
```

```bash
$ sum-buddy --input-dir examples/example_content --output-file examples/checksums.csv --ignore-file examples/.sbignore_all_except_dots --algorithm md5
Calculating checksums: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [00:00<00:00, 2178.48it/s]
Checksums written to examples/checksums.csv
cat examples/checksums.csv 
filepath,filename,md5
examples/example_content/.hidden_file,.hidden_file,d41d8cd98f00b204e9800998ecf8427e
examples/example_content/.hidden_dir/.hidden_file,.hidden_file,d41d8cd98f00b204e9800998ecf8427e
examples/example_content/.hidden_dir/file.txt,file.txt,7d52c7437e9af58dac029dd11b1024df
```

You may explore the filtering capabilities of the `--ignore-file` and `--include-file` options by using the provided example files under `examples/` and the CSV output files in `examples/expected_outputs/`.


### Python Package Usage
We expose three functions to be used in your Python code:
- `get_checksums`: Works like the CLI.
- `gather_file_paths`: Returns a list of file paths according to ignore/include patterns.
- `checksum`: Returns the checksum of a single file.

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
# or checksum = checksum("path/to/file", algorithm)
```

