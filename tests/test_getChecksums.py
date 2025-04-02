import unittest
from unittest.mock import patch, mock_open
import os
from io import StringIO

from sumbuddy import get_checksums

class TestGetChecksums(unittest.TestCase):

    def setUp(self):
        self.input_path = 'input_path'
        self.output_filepath = 'output.csv'
        self.ignore_file = 'ignore_patterns.txt'
        self.mock_file_paths = ['file1.txt', 'file2.txt', '.hidden_file']
        self.algorithm = 'md5'
        self.dummy_checksum = 'dummychecksum'

    @patch('os.path.isfile', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('sumbuddy.Hasher.checksum_file', return_value='dummychecksum')
    def test_get_checksums_single_file_to_file(self, mock_checksum, mock_open, mock_isfile):
        get_checksums(self.input_path, self.output_filepath, ignore_file=None, include_hidden=False, algorithm=self.algorithm)
        
        mock_open.assert_called_with(self.output_filepath, 'w', newline='')
        handle = mock_open()
        handle.write.assert_any_call('filepath,filename,md5\r\n')
        handle.write.assert_any_call(f'{self.input_path},{os.path.basename(self.input_path)},dummychecksum\r\n')

    @patch('os.path.isfile', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('sumbuddy.Hasher.checksum_file', return_value='dummychecksum')
    def test_get_checksums_single_file_to_stdout(self, mock_checksum, mock_open, mock_isfile):
        output_stream = StringIO()
        with patch('sys.stdout', new=output_stream):
            get_checksums(self.input_path, output_filepath=None, ignore_file=None, include_hidden=False, algorithm=self.algorithm)
            
        output = output_stream.getvalue()
        self.assertIn('filepath,filename,md5', output)
        self.assertIn(f'{self.input_path},{os.path.basename(self.input_path)},dummychecksum', output)

    @patch('os.path.abspath', side_effect=lambda x: x)
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('sumbuddy.Mapper.gather_file_paths', return_value=['file1.txt', 'file2.txt'])
    @patch('sumbuddy.Hasher.checksum_file', side_effect=lambda x, **kwargs: 'dummychecksum')
    def test_get_checksums_to_file(self, mock_checksum, mock_gather, mock_open, mock_exists, mock_abspath):
        get_checksums(self.input_path, self.output_filepath, ignore_file=None, include_hidden=False, algorithm=self.algorithm)
        
        mock_open.assert_called_with(self.output_filepath, 'w', newline='')
        handle = mock_open()
        handle.write.assert_any_call('filepath,filename,md5\r\n')
        handle.write.assert_any_call('file1.txt,file1.txt,dummychecksum\r\n')
        handle.write.assert_any_call('file2.txt,file2.txt,dummychecksum\r\n')
        
    @patch('os.path.abspath', side_effect=lambda x: x)
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('sumbuddy.Mapper.gather_file_paths', return_value=['file1.txt', 'file2.txt'])
    @patch('sumbuddy.Hasher.checksum_file', side_effect=lambda x, **kwargs: 'dummychecksum')
    def test_get_checksums_to_stdout(self, mock_checksum, mock_gather, mock_open, mock_exists, mock_abspath):
        output_stream = StringIO()
        with patch('sys.stdout', new=output_stream):
            get_checksums(self.input_path, output_filepath=None, ignore_file=None, include_hidden=False, algorithm=self.algorithm)
            
        output = output_stream.getvalue()
        self.assertIn('filepath,filename,md5', output)
        self.assertIn('file1.txt,file1.txt,dummychecksum', output)
        self.assertIn('file2.txt,file2.txt,dummychecksum', output)
        
    @patch('os.path.abspath', side_effect=lambda x: x)
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('sumbuddy.Mapper.gather_file_paths', return_value=['file1.txt', 'file2.txt'])
    @patch('sumbuddy.Hasher.checksum_file', side_effect=lambda x, **kwargs: 'dummychecksum')
    def test_get_checksums_with_ignore_file(self, mock_checksum, mock_gather, mock_open, mock_exists, mock_abspath):
        get_checksums(self.input_path, output_filepath=None, ignore_file=self.ignore_file, include_hidden=False, algorithm=self.algorithm)
        mock_gather.assert_called_with(self.input_path, ignore_file=self.ignore_file, include_hidden=False)
        
    @patch('os.path.abspath', side_effect=lambda x: x)
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('sumbuddy.Mapper.gather_file_paths', return_value=['file1.txt', 'file2.txt', '.hidden_file'])
    @patch('sumbuddy.Hasher.checksum_file', side_effect=lambda x, **kwargs: 'dummychecksum')
    def test_get_checksums_include_hidden(self, mock_checksum, mock_gather, mock_open, mock_exists, mock_abspath):
        get_checksums(self.input_path, output_filepath=None, ignore_file=None, include_hidden=True, algorithm=self.algorithm)
        mock_gather.assert_called_with(self.input_path, ignore_file=None, include_hidden=True)
        
    @patch('os.path.abspath', side_effect=lambda x: x)
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('sumbuddy.Mapper.gather_file_paths', return_value=['file1.txt', 'file2.txt'])
    @patch('sumbuddy.Hasher.checksum_file', side_effect=lambda x, **kwargs: 'dummychecksum')
    def test_get_checksums_different_algorithm(self, mock_checksum, mock_gather, mock_open, mock_exists, mock_abspath):
        algorithm = 'sha256'
        get_checksums(self.input_path, output_filepath=None, ignore_file=None, include_hidden=False, algorithm=algorithm)
        
        output_stream = StringIO()
        with patch('sys.stdout', new=output_stream):
            get_checksums(self.input_path, output_filepath=None, ignore_file=None, include_hidden=False, algorithm=algorithm)
            
        output = output_stream.getvalue()
        self.assertIn(f'filepath,filename,{algorithm}', output)
        self.assertIn('file1.txt,file1.txt,dummychecksum', output)
        self.assertIn('file2.txt,file2.txt,dummychecksum', output)

    @patch('os.path.abspath', side_effect=lambda x: x)
    @patch('os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    @patch('sumbuddy.Mapper.gather_file_paths', return_value=[])
    def test_get_checksums_empty_directory(self, mock_gather, mock_open, mock_exists, mock_abspath):
        output_stream = StringIO()
        with patch('sys.stdout', new=output_stream):
            get_checksums(self.input_path, output_filepath=None, ignore_file=None, include_hidden=False, algorithm=self.algorithm)
            
        output = output_stream.getvalue()
        self.assertIn('filepath,filename,md5', output)

    @patch('os.path.abspath', side_effect=lambda x: x)
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open)
    @patch('sumbuddy.Mapper.gather_file_paths', return_value=['file1.txt', 'file2.txt'])
    def test_get_checksums_invalid_algorithm(self, mock_gather, mock_open, mock_exists, mock_abspath):
        with self.assertRaises(ValueError):
            get_checksums(self.input_path, output_filepath=None, ignore_file=None, include_hidden=False, algorithm='invalid_alg')

if __name__ == '__main__':
    unittest.main()
