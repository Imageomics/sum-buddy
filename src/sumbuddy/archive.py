import os
import zipfile
import tempfile
import shutil

class ArchiveHandler:
    def __init__(self):
        self.temp_dir = None

    def process_zip(self, zip_path, root_dir):
        """
        Process a zip file and return paths to its contents.
        
        Parameters:
        ------------
        zip_path - String. Path to the zip file.
        root_dir - String. Root directory for relative path calculations.
        
        Returns:
        ---------
        List of tuples (file_path, relative_path) for files in the zip.
        """
        if not zipfile.is_zipfile(zip_path):
            return []

        # Create a temporary directory for extraction
        self.temp_dir = tempfile.mkdtemp()
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract all contents to temp directory
                zip_ref.extractall(self.temp_dir)
                
                # Get list of all files in the zip
                file_paths = []
                for member in zip_ref.namelist():
                    # Only add files, not directories
                    if member.endswith('/'):
                        continue
                    full_path = os.path.join(self.temp_dir, member)
                    # The path as it should appear in the CSV: zip_path/member
                    rel_path = f"{zip_path}/{member}"
                    file_paths.append((full_path, rel_path))
                return file_paths
        except Exception as e:
            self.cleanup()
            raise e

    def cleanup(self):
        """Clean up temporary directory if it exists."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None

    @staticmethod
    def stream_zip(zip_path):
        """
        Yield (name, file-like object) for each file in the ZIP archive.
        Only yields regular files (not directories).
        """
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if member.endswith('/'):
                    continue  # skip directories
                yield member, zip_ref.open(member) 