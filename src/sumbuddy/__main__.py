import argparse
import os
import hashlib
import csv
import fnmatch
from tqdm import tqdm

def md5_checksum(file_path):
    """
    Calculate the MD5 checksum of a file
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def read_patterns(filepath):
    """
    Read patterns from an include or ignore file, one pattern per line
    """
    with open(filepath, 'r') as f:
        patterns = [line.strip() for line in f if line.strip()]
    return patterns


def should_include(filepath, patterns, root, include_mode=False):
    """
    Determine if a file should be included based on patterns and the root directory.
    Excludes hidden files and directories by default unless explicitly included.
    """
    relative_filepath = os.path.relpath(filepath, start=root)

    # Default behavior when no patterns are passed: exclude all hidden files and directories
    if not patterns:
        return not relative_filepath.split(os.sep)[0].startswith('.')

    # Handle include mode
    if include_mode:
        # Include files that match any pattern
        return any(fnmatch.fnmatch(relative_filepath, pattern) for pattern in patterns)

    # Handle exclude mode with negation
    for pattern in patterns:
        if pattern.startswith('!'):
            if fnmatch.fnmatch(relative_filepath, pattern[1:]):
                # Negation pattern matches, include this file
                return True  

    # Handle exclude mode
    for pattern in patterns:
        if fnmatch.fnmatch(relative_filepath, pattern):
            # Pattern matches for ignore, exclude this file
            return False  

    return not relative_filepath.split(os.sep)[0].startswith('.')


def gather_file_paths(input_directory, output_filepath, ignore_patterns=None, include_patterns=None):
    """
    Gather file paths in the input directory, excluding the output file and applying pattern rules.
    """
    file_paths = []
    # Get the absolute path of the input directory
    root_directory = os.path.abspath(input_directory)
    # Get the absolute path of the output file
    output_file_abs_path = os.path.abspath(output_filepath)  

    for root, dirs, files in os.walk(input_directory):
        for name in files:
            file_path = os.path.join(root, name)
            if os.path.abspath(file_path) == output_file_abs_path:
                continue  # Skip the output file
            if (ignore_patterns or include_patterns):
                if include_patterns and should_include(file_path, include_patterns, root_directory, True):
                    file_paths.append(file_path)
                elif ignore_patterns and should_include(file_path, ignore_patterns, root_directory):
                    file_paths.append(file_path)
            else:
                # Apply default exclusion behavior when no patterns are provided
                if should_include(file_path, [], root_directory):
                    file_paths.append(file_path)

    return file_paths


def get_checksums(input_directory, output_filepath, ignore_patterns=None, include_patterns=None):
    """
    Generate a CSV file with the filepath, filename, and checksum of all files in the input directory according to patterns to ignore or include.
    """

    file_paths = gather_file_paths(input_directory, output_filepath, ignore_patterns, include_patterns)

    with open(output_filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filepath", "filename", "md5"])

        for file_path in tqdm(file_paths, desc="MD5ing"):
            checksum = md5_checksum(file_path)
            writer.writerow([file_path, os.path.basename(file_path), checksum])

    print(f"Checksums written to {output_filepath}")


def main():
    parser = argparse.ArgumentParser(description="Generate CSV with filepath, filename, and MD5 checksums for all files in a given directory")
    parser.add_argument("--input-dir", required=True, help="Directory to traverse for files")
    parser.add_argument("--output-file", required=True, help="Filepath for the output CSV file")
    parser.add_argument("--ignore-file", help="Filepath for the ignore patterns file")
    parser.add_argument("--include-file", help="Filepath for the include patterns file")

    args = parser.parse_args()

    if args.ignore_file and args.include_file:
        parser.error("Cannot use --ignore-file and --include-file simultaneously")

    ignore_patterns = read_patterns(args.ignore_file) if args.ignore_file else None
    include_patterns = read_patterns(args.include_file) if args.include_file else None

    get_checksums(args.input_dir, args.output_file, ignore_patterns, include_patterns)

if __name__ == "__main__":
    main()

