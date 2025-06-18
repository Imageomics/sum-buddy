import pytest
import tempfile
import os
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from sumbuddy.archive import ArchiveHandler
from sumbuddy.mapper import Mapper
from sumbuddy.hasher import Hasher


class TestArchiveHandler:
    """Test cases for ArchiveHandler class."""

    def test_process_zip_success(self):
        """Test successful zip file processing."""
        handler = ArchiveHandler()
        test_zip_path = Path(__file__).parent / "test_archive.zip"
        
        # Ensure test zip exists
        assert test_zip_path.exists(), "Test zip file not found"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            extracted_files = handler.process_zip(str(test_zip_path), temp_dir)
            
            # Should return list of tuples (file_path, relative_path)
            assert len(extracted_files) == 2
            assert any("test_file.txt" in str(f[1]) for f in extracted_files)
            assert any("nested_file.txt" in str(f[1]) for f in extracted_files)
            
            # Check that files were actually extracted
            for file_path, _ in extracted_files:
                assert Path(file_path).exists()

    def test_process_zip_invalid_file(self):
        """Test processing non-zip file."""
        handler = ArchiveHandler()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a non-zip file
            non_zip_file = Path(temp_dir) / "not_a_zip.txt"
            non_zip_file.write_text("This is not a zip file")
            
            # Should return empty list for non-zip files
            result = handler.process_zip(str(non_zip_file), temp_dir)
            assert result == []

    def test_process_zip_nonexistent_file(self):
        """Test processing non-existent file."""
        handler = ArchiveHandler()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent_file = Path(temp_dir) / "nonexistent.zip"
            
            # Should return empty list for non-existent files
            result = handler.process_zip(str(non_existent_file), temp_dir)
            assert result == []


class TestMapperWithZip:
    """Test cases for Mapper class with zip file support."""

    def test_gather_file_paths_with_zip(self):
        """Test gathering file paths including zip files."""
        mapper = Mapper()
        test_zip_path = Path(__file__).parent / "test_archive.zip"
        
        # Create a temporary directory with the test zip
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_zip_path = Path(temp_dir) / "test_archive.zip"
            # Copy test zip to temp directory
            import shutil
            shutil.copy2(test_zip_path, temp_zip_path)
            
            file_paths = mapper.gather_file_paths(temp_dir)
            
            # Should include the zip file itself
            assert str(temp_zip_path) in file_paths
            
            # Should include files from within the zip
            zip_file_paths = [p for p in file_paths if "test_archive.zip/" in p]
            assert len(zip_file_paths) == 2
            assert any("test_file.txt" in p for p in zip_file_paths)
            assert any("nested_file.txt" in p for p in zip_file_paths)

    def test_gather_file_paths_with_zip_and_filter(self):
        """Test gathering file paths with zip files and filters."""
        mapper = Mapper()
        test_zip_path = Path(__file__).parent / "test_archive.zip"
        
        # Create a temporary directory with the test zip
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_zip_path = Path(temp_dir) / "test_archive.zip"
            import shutil
            shutil.copy2(test_zip_path, temp_zip_path)
            
            # Create an ignore file to exclude nested files
            ignore_file = Path(temp_dir) / ".ignore"
            ignore_file.write_text("**/nested_dir/**")
            
            file_paths = mapper.gather_file_paths(temp_dir, ignore_file=str(ignore_file))
            
            # Should include the zip file itself
            assert str(temp_zip_path) in file_paths
            
            # Should include only non-nested files from zip
            zip_file_paths = [p for p in file_paths if "test_archive.zip/" in p]
            assert len(zip_file_paths) == 1
            assert any("test_file.txt" in p for p in zip_file_paths)
            assert not any("nested_file.txt" in p for p in zip_file_paths)


class TestHasherWithZip:
    """Test cases for Hasher class with zip file support."""

    def test_checksum_file_with_file_like_object(self):
        """Test checksum calculation with file-like object."""
        hasher = Hasher()
        test_zip_path = Path(__file__).parent / "test_archive.zip"
        
        # Test with zip file
        with zipfile.ZipFile(test_zip_path, 'r') as zip_file:
            # Get the first file in the zip
            file_name = zip_file.namelist()[0]
            with zip_file.open(file_name) as file_obj:
                checksum = hasher.checksum_file(file_obj)
                
                # Should return a valid checksum
                assert isinstance(checksum, str)
                assert len(checksum) > 0

    def test_checksum_file_with_zip_file_path(self):
        """Test checksum calculation with zip file path."""
        hasher = Hasher()
        test_zip_path = Path(__file__).parent / "test_archive.zip"
        
        checksum = hasher.checksum_file(str(test_zip_path))
        
        # Should return a valid checksum
        assert isinstance(checksum, str)
        assert len(checksum) > 0


def test_integration_zip_support():
    """Integration test for zip support functionality."""
    from sumbuddy import get_checksums
    import tempfile
    import csv
    
    test_zip_path = Path(__file__).parent / "test_archive.zip"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_zip_path = Path(temp_dir) / "test_archive.zip"
        import shutil
        shutil.copy2(test_zip_path, temp_zip_path)
        
        output_file = Path(temp_dir) / "checksums.csv"
        
        # Run get_checksums on directory containing zip
        get_checksums(temp_dir, output_file)
        
        # Verify output file was created
        assert output_file.exists()
        
        # Read and verify CSV contents
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Should have at least the zip file and its contents
            assert len(rows) >= 3
            
            # Should include zip file itself
            zip_rows = [r for r in rows if r['filename'] == 'test_archive.zip']
            assert len(zip_rows) == 1
            
            # Should include files from within zip
            zip_content_rows = [r for r in rows if 'test_archive.zip/' in r['filepath']]
            assert len(zip_content_rows) == 2
            
            # All rows should have valid checksums
            for row in rows:
                assert row['md5'] and len(row['md5']) > 0 