# sum-buddy
Command-line package to generate a CSV with filepath, filename, and checksum for contents of a given directory or a single file.

## Requirements
Python 3.10+


## Installation

```bash
pip install sum-buddy
```


## How it Works

### Command Line Usage

```
usage: sum-buddy [-h] [-o OUTPUT_FILE] [-i IGNORE_FILE | -H] [-a ALGORITHM] input_path

Generate CSV with filepath, filename, and checksums for all files in a given directory (or a single file)

positional arguments:
  input_path             File or directory to traverse for files

options:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Filepath for the output CSV file
  -i IGNORE_FILE, --ignore-file IGNORE_FILE
                        Filepath for the ignore patterns file
  -H, --include-hidden  Include hidden files
  -a ALGORITHM, --algorithm ALGORITHM
                        Hash algorithm to use (default: md5; available: ripemd160, sha3_224, sha512_224, blake2b, sha384, sha256, sm3, sha3_256, shake_256, sha512, sha1, sha224, md5, md5-sha1, sha3_384, sha3_512, sha512_256, shake_128, blake2s)
  -l LENGTH, --length LENGTH
                        Length of the digest for SHAKE (required) or BLAKE (optional) algorithms in bytes
```

> Note: The available algorithms are determined by those available to `hashlib` and may vary depending on your system and OpenSSL version, so the set shown on your system with `sum-buddy -h` may be different from above. At a minimum, it should include: `{blake2s, blake2b, md5, sha1, sha224, sha256, sha384, sha512, sha3_224, sha3_256, sha3_384, sha3_512, shake_128, shake_256}`, which is given by `hashlib.algorithms_guaranteed`.

#### CLI Examples

- **Basic Usage:**
```bash
sum-buddy examples/example_content/
```
> Output
> ```console
> filepath,filename,md5
> examples/example_content/file.txt,file.txt,7d52c7437e9af58dac029dd11b1024df
> examples/example_content/dir/file.txt,file.txt,7d52c7437e9af58dac029dd11b1024df
> ```

- **Output to File:**
```bash
sum-buddy --output-file examples/checksums.csv examples/example_content/
```
> Output
> ```console
> Calculating md5 checksums on examples/example_content/: 100%|███████████████████████████████████████████████████████████████████████████| 2/2 [00:00<00:00, 1552.01it/s]
> md5 checksums for examples/example_content/ written to examples/checksums.csv
> ```
```bash
cat examples/checksums.csv
```
> Output:
> ```console
> filepath,filename,md5
> examples/example_content/file.txt,file.txt,7d52c7437e9af58dac029dd11b1024df
> examples/example_content/dir/file.txt,file.txt,7d52c7437e9af58dac029dd11b1024df
> ```

- **Ignore Contents Based on Patterns:**
```bash
sum-buddy --output-file examples/checksums.csv --ignore-file examples/.sbignore_except_txt examples/example_content/
```
> Output
> ```console
> Calculating md5 checksums on examples/example_content/: 100%|████████████████████████████████████████████████████████████████████████████████████| 4/4 [00:00<00:00, 1845.48it/s]
> md5 checksums for examples/example_content/ written to examples/checksums.csv
>```
```bash
cat examples/checksums.csv
```
> Output:
> ```console
> filepath,filename,md5
> examples/example_content/file.txt,file.txt,7d52c7437e9af58dac029dd11b1024df
> examples/example_content/.hidden_dir/file.txt,file.txt,7d52c7437e9af58dac029dd11b1024df
> examples/example_content/dir/file.txt,file.txt,7d52c7437e9af58dac029dd11b1024df
> examples/example_content/dir/.hidden_dir/file.txt,file.txt,7d52c7437e9af58dac029dd11b1024df
>```
- **Include Hidden Files:**
```bash
sum-buddy --output-file examples/checksums.csv --include-hidden examples/example_content/
```
> Output
> ```console
> Calculating md5 checksums on examples/example_content/: 100%|████████████████████████████████████████████████████████████████████████████| 8/8 [00:00<00:00, 2101.35it/s]
> md5 checksums for examples/example_content/ written to examples/checksums.csv
> ```

```bash
cat examples/checksums.csv
```
> Output:
> ```console
> filepath,filename,md5
> examples/example_content/.hidden_file,.hidden_file,d41d8cd98f00b204e9800998ecf8427e
> examples/example_content/file.txt,file.txt,7d52c7437e9af58dac029dd11b1024df
> examples/example_content/.hidden_dir/.hidden_file,.hidden_file,d41d8cd98f00b204e9800998ecf8427e
> examples/example_content/.hidden_dir/file.txt,file.txt,7d52c7437e9af58dac029dd11b1024df
> examples/example_content/dir/.hidden_file,.hidden_file,d41d8cd98f00b204e9800998ecf8427e
> examples/example_content/dir/file.txt,file.txt,7d52c7437e9af58dac029dd11b1024df
> examples/example_content/dir/.hidden_dir/.hidden_file,.hidden_file,d41d8cd98f00b204e9800998ecf8427e
> examples/example_content/dir/.hidden_dir/file.txt,file.txt,7d52c7437e9af58dac029dd11b1024df
>```


If only a target directory is passed, the default settings are to ignore hidden files and directories (those that begin with a `.`), use the `md5` algorithm, and print output to `stdout`, which can be piped (`|`).

To include all files and directories, including hidden ones, use the `--include-hidden` (or `-H`) option.

To ignore files based on patterns, use the `--ignore-file` (or `-i`) option with the path to a file containing patterns to ignore. The `--ignore-file` works identically to how `git` handles a `.gitignore` file using the implementation from [pathspec](https://github.com/cpburnz/python-pathspec).

You may explore the filtering capabilities of the `--ignore-file` option by using the provided example files under `examples/` and pointing at `examples/example_content`. The expected CSV output files are provided in `examples/expected_outputs/`.

The `bash` script, `examples/run_examples` will run all the examples; it was used to generate the `expected_outputs`.

### Python Package Usage
We expose three functions to be used in your Python code:
- `get_checksums`: Works like the CLI.
- `gather_file_paths`: Returns a list of file paths according to ignore patterns.
- `checksum_file`: Returns the checksum of a single file.

```python
from sumbuddy import get_checksums, gather_file_paths, checksum_file

input_path = "examples/example_content"
output_file = "examples/checksums.csv"
include_hidden = True        # Optional
ignore_file = "examples/.sbignore_except_txt"   # Optional
alg = "md5"           # Optional, possible inputs include list elements returned by hashlib.algorithms_available

# To generate checksums and save to a CSV file
get_checksums(input_path, output_file, ignore_file=ignore_file, algorithm=alg)
# or get_checksums(input_path, output_file, ignore_hidden=ignore_hidden)
# or get_checksums(input_path, output_file)

# outputs status bar followed by
# Checksums written to examples/checksums.csv

# To gather a list of file paths according to ignore/include patterns
file_paths = gather_file_paths(input_path, ignore_file=ignore_file)
# or file_paths = gather_file_paths(input_path, include_hidden=include_hidden)
# or file_paths = gather_file_paths(input_path)

# To calculate the checksum of a single file
sum = checksum_file("examples/example_content/file.txt", algorithm=alg)
# or sum = checksum_file("examples/example_content/file.txt")
```

## Development
To develop the package further:

1. Clone the repository and create a branch
2. Install with dev dependencies:
```bash
pip install -e ".[dev]"
```
3. Install pre-commit hook
```bash
pre-commit install
pre-commit autoupdate # optionally update
```
4. Run tests:
```bash
pytest
```
