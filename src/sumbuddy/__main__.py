import argparse
from sumbuddy.hasher import Hasher
from sumbuddy.mapper import Mapper
from sumbuddy.exceptions import EmptyInputDirectoryError, NoFilesAfterFilteringError, LengthUsedForFixedLengthHashError
import csv
import hashlib
from tqdm import tqdm
import sys
import os

def get_checksums(input_path, output_filepath=None, ignore_file=None, include_hidden=False, algorithm='md5', length=None):
    """
    Generate a CSV file with the filepath, filename, and checksum of all files in the input directory according to patterns to ignore. Checksum column is labeled by the selected algorithm (e.g., 'md5' or 'sha256').
    
    Parameters:
    ------------
    input_path - String. File or directory to traverse for files.
    output_filepath - String [optional]. Filepath for the output CSV file. Defaults to None, i.e. output will be to stdout.
    ignore_file - String [optional]. Filepath for the ignore patterns file.
    include_hidden - Boolean [optional]. Whether to include hidden files. Default is False.
    algorithm - String. Algorithm to use for checksums. Default: 'md5', see options with 'hashlib.algorithms_available'.
    length - Integer [conditionally optional]. Length of the digest for SHAKE (required) and BLAKE (optional) algorithms in bytes.
    """
    mapper = Mapper()

    if os.path.isfile(input_path):
        file_paths = [input_path]
        if ignore_file:
            print("Warning: --ignore-file (-i) flag is ignored when input is a single file.")
        if include_hidden:
            print("Warning: --include-hidden (-H) flag is ignored when input is a single file.")
    else:
        try:
            file_paths = mapper.gather_file_paths(input_path, ignore_file=ignore_file, include_hidden=include_hidden)
        except (EmptyInputDirectoryError, NoFilesAfterFilteringError) as e:
            sys.exit(str(e))

    # Exclude the output file from being hashed
    if output_filepath:
        output_file_abs_path = os.path.abspath(output_filepath)
        file_paths = [path for path in file_paths if os.path.abspath(path) != output_file_abs_path]

    hasher = Hasher(algorithm)
    output_stream = open(output_filepath, 'w', newline='') if output_filepath else sys.stdout

    try:
        writer = csv.writer(output_stream)
        writer.writerow(["filepath", "filename", f"{algorithm}"])

        disable_tqdm = output_filepath is None
        for file_path in tqdm(file_paths, desc=f"Calculating {algorithm} checksums on {input_path}", disable=disable_tqdm):
            checksum = hasher.checksum_file(file_path, algorithm=algorithm, length=length)
            writer.writerow([file_path, os.path.basename(file_path), checksum])

    finally:
        if output_filepath:
            output_stream.close()

    if output_filepath:     
        print(f"{algorithm} checksums for {input_path} written to {output_filepath}")

def main():

    available_algorithms = ', '.join(hashlib.algorithms_available)
    
    parser = argparse.ArgumentParser(description="Generate CSV with filepath, filename, and checksums for all files in a given directory (or a single file)")
    parser.add_argument("input_path", help="File or directory to traverse for files")
    parser.add_argument("-o", "--output-file", help="Filepath for the output CSV file; defaults to stdout", default=None)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-i", "--ignore-file", help="Filepath for the ignore patterns file")
    group.add_argument("-H", "--include-hidden", action="store_true", help="Include hidden files")
    parser.add_argument("-a", "--algorithm", default="md5", help=f"Hash algorithm to use (default: md5; available: {available_algorithms})")
    parser.add_argument("-l", "--length", type=int, help="Length of the digest for SHAKE (required) or BLAKE (optional) algorithms in bytes")

    args = parser.parse_args()

    if args.output_file and not args.output_file.endswith('.csv'):
        parser.error("Output file is in CSV format; extension should be '.csv'")

    if args.output_file and os.path.exists(args.output_file):
        overwrite = input(f"Output file '{args.output_file}' already exists. Overwrite? [y/n]: ")
        if overwrite.lower() != 'y':
            sys.exit("Exited without executing")
        
    try:
        get_checksums(args.input_path, args.output_file, args.ignore_file, args.include_hidden, args.algorithm, args.length)
    except (LengthUsedForFixedLengthHashError) as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
