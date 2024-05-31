import os
from sumbuddy.filter import Filter

class Mapper:
    def __init__(self):
        self.filter_manager = Filter()

    def reset_filter(self, ignore_file=None, ignore_hidden=False):
        """
        Reset the filter manager with new ignore patterns.
        
        Parameters:
        ------------
        ignore_file - String [optional]. Filepath for the ignore patterns file.
        ignore_hidden - Boolean [optional]. Whether to ignore hidden files.
        """
        self.filter_manager = Filter()
        if ignore_file:
            self.filter_manager.read_patterns(filepath=ignore_file)
        elif ignore_hidden is True:
            self.filter_manager.read_patterns(ignore_hidden=True)
        elif ignore_hidden is False:
            self.filter_manager.read_patterns()  # Reset to include everything

    def gather_file_paths(self, input_directory, ignore_file=None, ignore_hidden=None):
        """
        Generate list of file paths in the input directory based on pattern rules (ignore).
        
        Parameters:
        ------------
        input_directory - String. Directory to traverse for files.
        ignore_file - String [optional]. Filepath for the ignore patterns file.
        ignore_hidden - Boolean [optional]. Whether to ignore hidden files.
        
        Returns:
        ---------
        file_paths - List. Files in input_directory that are not ignored.
        """
        self.reset_filter(ignore_file=ignore_file, ignore_hidden=ignore_hidden)
        
        file_paths = []
        root_directory = os.path.abspath(input_directory)

        for root, dirs, files in os.walk(input_directory):
            for name in files:
                file_path = os.path.join(root, name)
                if self.filter_manager.should_include(file_path, root_directory):
                    file_paths.append(file_path)

        return file_paths
    