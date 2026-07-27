class EmptyInputDirectoryError(Exception):
    def __init__(self, input_directory):
        message = f"The directory {input_directory} and subdirectories (if any) contain no files. \nPlease provide a directory with files."
        super().__init__(message)

class NotADirectoryError(Exception):
    def __init__(self, input_directory):
        message = f"The input path '{input_directory}' is not a directory. \nPlease provide a directory with files."
        super().__init__(message)

class NoFilesAfterFilteringError(Exception):
    def __init__(self, input_directory, ignore_file):
        message = f"The directory {input_directory} contains files, but all are filtered out. \nCheck patterns in your {ignore_file} file and/or hidden files settings."
        super().__init__(message)

class LengthUsedForFixedLengthHashError(Exception):
    def __init__(self, algorithm):
        message = f"Length paremeter is not applicable for fixed-length algorithm '{algorithm}'."
        super().__init__(message)

class OutputFileExistsError(FileExistsError):
    def __init__(self, output_filepath):
        message = f"The output file '{output_filepath}' already exists. \nPass force=True (Python) or use the -f/--force flag (CLI) to overwrite it."
        super().__init__(message)
