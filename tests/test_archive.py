import tempfile
import zipfile
from pathlib import Path

from sumbuddy.archive import ArchiveHandler
from sumbuddy.mapper import Mapper
from sumbuddy.hasher import Hasher


class TestArchiveHandler:
    """Test cases for ArchiveHandler class."""

    def test_stream_zip_success(self):
        """Test streaming files from a zip archive."""
        test_zip_path = Path(__file__).parent / "test_archive.zip"
        assert test_zip_path.exists(), "Test zip file not found"
        members = list(ArchiveHandler.stream_zip(str(test_zip_path)))
        assert len(members) == 2
        names = [name for name, _ in members]
        assert any("test_file.txt" in n for n in names)
        assert any("nested_file.txt" in n for n in names)
        # Check that file-like objects are readable
        for name, file_obj in members:
            content = file_obj.read()
            assert isinstance(content, bytes)
            file_obj.close()

    def test_stream_zip_invalid_file(self):
        """Test streaming from a non-zip file raises BadZipFile."""
        with tempfile.TemporaryDirectory() as temp_dir:
            non_zip_file = Path(temp_dir) / "not_a_zip.txt"
            non_zip_file.write_text("This is not a zip file")
            try:
                list(ArchiveHandler.stream_zip(str(non_zip_file)))
            except zipfile.BadZipFile:
                pass  # Expected
            else:
                assert False, "Expected zipfile.BadZipFile to be raised for non-zip file"


class TestMapperWithZip:
    """Test cases for Mapper class with zip file support."""

    def test_gather_file_paths_with_zip(self):
        """Test gathering file paths including zip files."""
        mapper = Mapper()
        test_zip_path = Path(__file__).parent / "test_archive.zip"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_zip_path = Path(temp_dir) / "test_archive.zip"
            import shutil
            shutil.copy2(test_zip_path, temp_zip_path)
            regular_files, zip_archives = mapper.gather_file_paths(temp_dir)
            assert str(temp_zip_path) in zip_archives
            assert isinstance(regular_files, list)
            assert isinstance(zip_archives, list)

    def test_gather_file_paths_with_zip_and_filter(self):
        """Test gathering file paths with zip files and filters."""
        mapper = Mapper()
        test_zip_path = Path(__file__).parent / "test_archive.zip"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_zip_path = Path(temp_dir) / "test_archive.zip"
            import shutil
            shutil.copy2(test_zip_path, temp_zip_path)
            ignore_file = Path(temp_dir) / ".ignore"
            ignore_file.write_text("**/nested_dir/**")
            regular_files, zip_archives = mapper.gather_file_paths(temp_dir, ignore_file=str(ignore_file))
            assert str(temp_zip_path) in zip_archives
            assert isinstance(regular_files, list)
            assert isinstance(zip_archives, list)


class TestHasherWithZip:
    """Test cases for Hasher class with zip file support."""

    def test_checksum_file_with_file_like_object(self):
        """Test checksum calculation with file-like object."""
        hasher = Hasher()
        test_zip_path = Path(__file__).parent / "test_archive.zip"
        with zipfile.ZipFile(test_zip_path, 'r') as zip_file:
            file_name = zip_file.namelist()[0]
            with zip_file.open(file_name) as file_obj:
                checksum = hasher.checksum_file(file_obj)
                assert isinstance(checksum, str)
                assert len(checksum) > 0

    def test_checksum_file_with_zip_file_path(self):
        """Test checksum calculation with zip file path."""
        hasher = Hasher()
        test_zip_path = Path(__file__).parent / "test_archive.zip"
        checksum = hasher.checksum_file(str(test_zip_path))
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
        get_checksums(temp_dir, output_file)
        assert output_file.exists()
        with open(output_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) >= 3
            zip_rows = [r for r in rows if r['filename'] == 'test_archive.zip']
            assert len(zip_rows) == 1
            zip_content_rows = [r for r in rows if 'test_archive.zip/' in r['filepath']]
            assert len(zip_content_rows) == 2
            for row in rows:
                assert row['md5'] and len(row['md5']) > 0 