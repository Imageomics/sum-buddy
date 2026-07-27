import os

from sumbuddy.archive import ArchiveHandler
from sumbuddy.exceptions import (
    EmptyInputDirectoryError,
    NoFilesAfterFilteringError,
    NotADirectoryError,
)
from sumbuddy.filter import Filter


class Mapper:
    def __init__(self):
        self.filter_manager = Filter()
        self.archive_handler = ArchiveHandler()

    def reset_filter(self, ignore_file=None, include_hidden=False):
        """
        Reset the filter manager with new ignore patterns.

        Parameters:
        ------------
        ignore_file - String [optional]. Filepath for the ignore patterns file.
        include_hidden - Boolean [optional]. Whether to include hidden files.
        """

        self.filter_manager = Filter()

        if ignore_file:
            self.filter_manager.read_ignore_patterns(ignore_filepath=ignore_file)
        elif include_hidden:
            self.filter_manager.read_ignore_patterns(include_hidden=True)  # No default ignore patterns
        else:
            self.filter_manager.read_ignore_patterns(include_hidden=False)  # Default: ignore hidden files

    def gather_file_paths(self, input_directory, ignore_file=None, include_hidden=False, archive_dive=True):
        """
        Generate list of file paths in the input directory based on ignore pattern rules.

        Parameters:
        ------------
        input_directory - String. Directory to traverse for files.
        ignore_file - String [optional]. Filepath for the ignore patterns file.
        include_hidden - Boolean [optional]. Whether to include hidden files.
        archive_dive - Boolean [optional]. Whether to classify supported archives separately so callers can descend into their members. When False, archive files are returned with regular_files. Default is True.

        Returns:
        ---------
        regular_files - List. Files in input_directory that are not ignored. When archive_dive is True, this excludes supported archives. When False, it includes them.
        archive_files - List. Archive files in input_directory that are not ignored and should be expanded by the caller.
        """

        if not os.path.isdir(input_directory):
            raise NotADirectoryError(input_directory)

        self.reset_filter(ignore_file=ignore_file, include_hidden=include_hidden)

        regular_files = []
        archive_files = []
        root_directory = os.path.abspath(input_directory)
        has_files = False

        for root, dirs, files in os.walk(input_directory):
            if files:
                has_files = True
            for name in files:
                file_path = os.path.normpath(os.path.join(root, name))
                if self.filter_manager.should_include(file_path, root_directory):
                    if archive_dive and self.archive_handler.is_supported_archive(file_path):
                        archive_files.append(file_path)
                    else:
                        regular_files.append(file_path)

        if not has_files:
            raise EmptyInputDirectoryError(input_directory)
        if not (regular_files or archive_files):
            raise NoFilesAfterFilteringError(input_directory, ignore_file)

        return regular_files, archive_files
