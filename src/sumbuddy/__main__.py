import argparse
from sumbuddy.hasher import Hasher
from sumbuddy.mapper import Mapper
from sumbuddy.filter import Filter
import csv
import hashlib
from tqdm import tqdm
import sys
import os

def get_checksums(input_directory, output_filepath=None, ignore_file=None, include_hidden=False, algorithm='md5'):
    """
    Generate a CSV file with the filepath, filename, and checksum of all files in the input directory according to patterns to ignore. Checksum column is labeled by the selected algorithm (e.g., 'md5' or 'sha256').
    
    Parameters:
    ------------
    input_directory - String. Directory to traverse for files.
    output_filepath - String [optional]. Filepath for the output CSV file. Defaults to None, i.e. output will be to stdout.
    ignore_file - String [optional]. Filepath for the ignore patterns file.
    include_hidden - Boolean [optional]. Whether to include hidden files. Default is False.
    algorithm - String. Algorithm to use for checksums. Default: 'md5', see options with 'hashlib.algorithms_available'.
    """
    mapper = Mapper()
    file_paths = mapper.gather_file_paths(input_directory, ignore_file=ignore_file, include_hidden=include_hidden)
    
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
        for file_path in tqdm(file_paths, desc=f"Calculating {algorithm} checksums on {input_directory}", disable=disable_tqdm):
            checksum = hasher.checksum_file(file_path)
            writer.writerow([file_path, os.path.basename(file_path), checksum])

    finally:
        if output_filepath:
            output_stream.close()

    if output_filepath:     
        print(f"{algorithm} checksums for {input_directory} written to {output_filepath}")

def main():

    available_algorithms = ', '.join(hashlib.algorithms_available)
        
    parser = argparse.ArgumentParser(description="Generate CSV with filepath, filename, and checksums for all files in a given directory")
    parser.add_argument("input_dir", help="Directory to traverse for files")
    parser.add_argument("-o", "--output-file", help="Filepath for the output CSV file; defaults to stdout", default=None)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-i", "--ignore-file", help="Filepath for the ignore patterns file")
    group.add_argument("-H", "--include-hidden", action="store_true", help="Include hidden files")
    parser.add_argument("-a", "--algorithm", default="md5", help=f"Hash algorithm to use (default: md5; available: {available_algorithms})")

    args = parser.parse_args()

    if args.output_file and not args.output_file.endswith('.csv'):
        parser.error("Output file is in CSV format; extension should be '.csv'")

    if args.output_file and os.path.exists(args.output_file):
        overwrite = input(f"Output file '{args.output_file}' already exists. Overwrite? [y/n]: ")
        if overwrite.lower() != 'y':
            sys.exit("Exited without executing")
        
    get_checksums(args.input_dir, args.output_file, args.ignore_file, args.include_hidden, args.algorithm)

if __name__ == "__main__":
    main()
