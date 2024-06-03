# sum-buddy
Command-line package to generate a CSV with filepath, filename, and checksum for contents of given directory.


## Requirements
Python 3.7+


## Installation

```bash
pip install git+https://github.com/Imageomics/sum-buddy
```


## How it Works

### Command Line Usage

```
usage: sum-buddy [-h] --input-dir INPUT_DIR --output-file OUTPUT_FILE [--ignore-file IGNORE_FILE] [--ignore-hidden] [--algorithm ALGORITHM]

Generate CSV with filepath, filename, and checksums for all files in a given directory

options:
  -h, --help            show this help message and exit
  --input-dir INPUT_DIR
                        Directory to traverse.
  --output-file OUTPUT_FILE
                        Filepath for the output CSV file.
  --ignore-file IGNORE_FILE
                        Filepath for the file with ignore patterns. Works like a .gitignore file.
  --ignore-hidden       Ignore hidden files (Use either this or --ignore-file. Identical to providing an ignore file with '.*')
  --algorithm ALGORITHM
                        Hash algorithm to use (default: md5, see options with 'hashlib.algorithms_available')
```

#### CLI Examples
You may use the `examples/` directory to test the CLI.

- **Ignore All:**
```bash
sum-buddy --input-dir examples/example_content --output-file examples/checksums.csv --ignore-file examples/.sbignore_all --algorithm md5
```
> Output
> ```console
> Calculating checksums: 0it [00:00, ?it/s]
> Checksums written to examples/checksums.csv
> ```
```bash
cat examples/checksums.csv
```
>  Output:
> ```console
> filepath,filename,md5
> ```

- **Ignore All but Dot Files:**
```bash
sum-buddy --input-dir examples/example_content --output-file examples/checksums.csv --ignore-file examples/.sbignore_all_except_dots --algorithm md5
```
> Output:
> ```console
> Calculating checksums: 100%|███████████████████████████████████████████████████████████████████████████████████████████████| 6/6 [00:00<00:00, 2496.36it/s]
> Checksums written to examples/checksums.csv
> ```
```bash
cat examples/checksums.csv
```
> Output:
> ```console
> filepath,filename,md5
> examples/example_content/.hidden_file,.hidden_file,d41d8cd98f00b204e9800998ecf8427e
> examples/example_content/.hidden_dir/.hidden_file,.hidden_file,d41d8cd98f00b204e9800998ecf8427e
> examples/example_content/.hidden_dir/file.txt,file.txt,7d52c7437e9af58dac029dd11b1024df
> examples/example_content/dir/.hidden_file,.hidden_file,d41d8cd98f00b204e9800998ecf8427e
> examples/example_content/dir/.hidden_dir/.hidden_file,.hidden_file,d41d8cd98f00b204e9800998ecf8427e
> examples/example_content/dir/.hidden_dir/file.txt,file.txt,7d52c7437e9af58dac029dd11b1024df
> ```

The `--ignore-file` works identically to how `git` handles a `.gitignore` file using the implementation from [pathspec](https://github.com/cpburnz/python-pathspec).

You may explore the filtering capabilities of the `--ignore-file` option by using the provided example files under `examples/` and pointing at `examples/example_content`. The expected CSV output files are provided in `examples/expected_outputs/`.

The `--ignore-hidden` option is a shortcut to ignore all hidden files. It is equivalent to providing an ignore file with the following content:
```
.*
```

### Python Package Usage
We expose three functions to be used in your Python code:
- `get_checksums`: Works like the CLI.
- `gather_file_paths`: Returns a list of file paths according to ignore patterns.
- `checksum`: Returns the checksum of a single file.

```python
from sumbuddy import get_checksums, gather_file_paths, checksum

input_dir = "./examples/example_content"
output_file = "./examples/checksums.csv"
ignore_hidden = True        # Optional
ignore_file = "./examples/.sbignore_except_txt"   # Optional
alg = "md5"           # Optional, possible inputs include list elements returned by hashlib.algorithms_available

# To generate checksums and save to a CSV file
get_checksums(input_dir, output_file, ignore_file=ignore_file, algorithm=alg)
# or get_checksums(input_dir, output_file, ignore_hidden=ignore_hidden)
# or get_checksums(input_dir, output_file)

# outputs status bar followed by
# Checksums written to ./examples/checksums.csv

# To gather a list of file paths according to ignore/include patterns
file_paths = gather_file_paths(input_dir, ignore_file=ignore_file)
# or file_paths = gather_file_paths(input_dir, ignore_hidden=ignore_hidden)
# or file_paths = gather_file_paths(input_dir)

# To calculate the checksum of a single file
sum = checksum("./examples/example_content/file.txt", algorithm=alg)
# or sum = checksum("./examples/example_content/file.txt")
```

