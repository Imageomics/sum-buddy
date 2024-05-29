import os
from sumbuddy.filter import Filter

class Mapper:
    def __init__(self, filter_manager=None):
        self.filter_manager = filter_manager or Filter()

    def gather_file_paths(self, input_directory, ignore_file=None, include_file=None):
        """
        Generate list of file paths in the input directory based on pattern rules (include or exclude).
        
        Parameters:
        ------------
        input_directory - String. Directory to traverse for files.
        ignore_file - String [optional]. Filepath for the ignore patterns file. Dotfiles are ignored by default and output file won't be hashed.
        include_file - String [optional]. Filepath for the include patterns file.
        
        Returns:
        ---------
        file_paths - List. Files in input_directory that are included (i.e., files matching  include_file patterns or not matching ignore_file patterns).
        """
        ignore_patterns = self.filter_manager.read_patterns(ignore_file) if ignore_file else None
        include_patterns = self.filter_manager.read_patterns(include_file) if include_file else None

        file_paths = []
        root_directory = os.path.abspath(input_directory)

        for root, dirs, files in os.walk(input_directory):
            for name in files:
                file_path = os.path.join(root, name)
                if (ignore_patterns or include_patterns):
                    if include_patterns and self.filter_manager.should_include(file_path, include_patterns, root_directory, True):
                        file_paths.append(file_path)
                    elif ignore_patterns and self.filter_manager.should_include(file_path, ignore_patterns, root_directory):
                        file_paths.append(file_path)
                else:
                    if self.filter_manager.should_include(file_path, [], root_directory):
                        file_paths.append(file_path)

        return file_paths
