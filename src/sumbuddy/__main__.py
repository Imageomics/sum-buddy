import argparse
from sumbuddy.hasher import Hasher
from sumbuddy.mapper import Mapper
from sumbuddy.filter import Filter
import csv
from tqdm import tqdm
import os

def get_checksums(input_directory, output_filepath, ignore_file=None, include_file=None):
    """
    Generate a CSV file with the filepath, filename, and checksum of all files in the input directory according to patterns to ignore or include.
    """
    filter_manager = Filter()
    mapper = Mapper(filter_manager)
    file_paths = mapper.gather_file_paths(input_directory, ignore_file, include_file)
    
    # Exclude the output file from being hashed
    output_file_abs_path = os.path.abspath(output_filepath)
    file_paths = [path for path in file_paths if os.path.abspath(path) != output_file_abs_path]

    hasher = Hasher()
    with open(output_filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filepath", "filename", "checksum"])

        for file_path in tqdm(file_paths, desc="Calculating checksums"):
            checksum = hasher.checksum(file_path)
            writer.writerow([file_path, os.path.basename(file_path), checksum])

    print(f"Checksums written to {output_filepath}")

def main():
    parser = argparse.ArgumentParser(description="Generate CSV with filepath, filename, and checksums for all files in a given directory")
    parser.add_argument("--input-dir", required=True, help="Directory to traverse for files")
    parser.add_argument("--output-file", required=True, help="Filepath for the output CSV file")
    parser.add_argument("--ignore-file", help="Filepath for the ignore patterns file")
    parser.add_argument("--include-file", help="Filepath for the include patterns file")

    args = parser.parse_args()

    if args.ignore_file and args.include_file:
        parser.error("Cannot use --ignore-file and --include-file simultaneously")

    get_checksums(args.input_dir, args.output_file, args.ignore_file, args.include_file)

if __name__ == "__main__":
    main()
