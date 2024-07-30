import os
from sumbuddy.filter import Filter
from sumbuddy.exceptions import EmptyInputDirectoryError, NoFilesAfterFilteringError, NotADirectoryError

class Mapper:
    def __init__(self):
        self.filter_manager = Filter()

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

    def gather_file_paths(self, input_directory, ignore_file=None, include_hidden=False):
        """
        Generate list of file paths in the input directory based on ignore pattern rules.
        
        Parameters:
        ------------
        input_directory - String. Directory to traverse for files.
        ignore_file - String [optional]. Filepath for the ignore patterns file.
        include_hidden - Boolean [optional]. Whether to include hidden files.
        
        Returns:
        ---------
        file_paths - List. Files in input_directory that are not ignored.
        """

        if not os.path.isdir(input_directory):
            raise NotADirectoryError(input_directory)
        
        self.reset_filter(ignore_file=ignore_file, include_hidden=include_hidden)
        
        file_paths = []
        root_directory = os.path.abspath(input_directory)
        has_files = False

        for root, dirs, files in os.walk(input_directory):
            if files:
                has_files = True
            for name in files:
                file_path = os.path.join(root, name)
                if self.filter_manager.should_include(file_path, root_directory):
                    file_paths.append(file_path)

        if not has_files:
            raise EmptyInputDirectoryError(input_directory)
        if not file_paths:
            raise NoFilesAfterFilteringError(input_directory, ignore_file)

        return file_paths
