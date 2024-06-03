import argparse
from sumbuddy.hasher import Hasher
from sumbuddy.mapper import Mapper
from sumbuddy.filter import Filter
import csv
from tqdm import tqdm
import os

def get_checksums(input_directory, output_filepath, ignore_file=None, ignore_hidden=None, algorithm='md5'):
    """
    Generate a CSV file with the filepath, filename, and checksum of all files in the input directory according to patterns to ignore. Checksum column is labeled by the selected algorithm (e.g., 'md5' or 'sha256').
    
    Parameters:
    ------------
    input_directory - String. Directory to traverse for files.
    output_filepath - String. Filepath for the output CSV file.
    ignore_file - String [optional]. Filepath for the ignore patterns file.
    ignore_hidden - Boolean [optional]. Whether to ignore hidden files. Default is False.
    algorithm - String. Algorithm to use for checksums. Default: 'md5', see options with 'hashlib.algorithms_available'.
    """
    mapper = Mapper()
    file_paths = mapper.gather_file_paths(input_directory, ignore_file=ignore_file, ignore_hidden=ignore_hidden)
    
    # Exclude the output file from being hashed
    output_file_abs_path = os.path.abspath(output_filepath)
    file_paths = [path for path in file_paths if os.path.abspath(path) != output_file_abs_path]

    hasher = Hasher(algorithm)
    with open(output_filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filepath", "filename", f"{algorithm}"])

        for file_path in tqdm(file_paths, desc="Calculating checksums"):
            checksum = hasher.checksum(file_path)
            writer.writerow([file_path, os.path.basename(file_path), checksum])

    print(f"Checksums written to {output_filepath}")

def main():
    parser = argparse.ArgumentParser(description="Generate CSV with filepath, filename, and checksums for all files in a given directory")
    parser.add_argument("--input-dir", required=True, help="Directory to traverse for files")
    parser.add_argument("--output-file", required=True, help="Filepath for the output CSV file")
    parser.add_argument("--ignore-file", help="Filepath for the ignore patterns file")
    parser.add_argument("--ignore-hidden", action="store_true", help="Ignore hidden files (Use either this or --ignore-file. Identical to providing an ignore file with '.*')")
    parser.add_argument("--algorithm", default="md5", help="Hash algorithm to use (default: md5, see options with 'hashlib.algorithms_available')")

    args = parser.parse_args()

    if args.ignore_file and args.ignore_hidden:
        parser.error("Only one of --ignore-file or --ignore-hidden can be used at a time.")

    get_checksums(args.input_dir, args.output_file, args.ignore_file, args.ignore_hidden, args.algorithm)

if __name__ == "__main__":
    main()
