import argparse
import os
import hashlib
import csv
from tqdm import tqdm

def md5_checksum(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_checksums(input_directory, output_filepath):
    with open(output_filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filepath", "filename", "md5"])
        for root, dirs, files in os.walk(input_directory):
            n_files = len(files)
            for name in tqdm(files, total=n_files, desc="MD5ing"):
                file_path = os.path.join(root, name)
                checksum = md5_checksum(file_path)
                writer.writerow([file_path, name, checksum])
        print(f"Checksums written to {output_filepath}")

def main():
    parser = argparse.ArgumentParser(description="Generate CSV with filepath, filename, and MD5 checksums for all files in a given directory") 
    parser.add_argument("--input-dir", required=True, help="Directory to traverse for files") 
    parser.add_argument("--output-file", required=True, help="Filepath for the output CSV file")
    args = parser.parse_args()
    get_checksums(args.input_dir, args.output_file)

if __name__ == "__main__":
    main()
