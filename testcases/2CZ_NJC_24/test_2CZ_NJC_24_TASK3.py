import io
import random
import re
import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
from statistics import fmean

from python_testcase_functions import NoMoreClosingFunction

from .outfile_3 import task3_1, task3_2, task3_3

resource_directory = Path(__file__).parent / 'Resources'

class TestTask3_1(unittest.TestCase):
    def test_sort(self):
        "Test task 3.1 with random 100 random integers"
        arr = random.choices(range(1000), k=100)
        with patch('sys.stdout'):
            self.assertEqual(task3_1(arr), sorted(arr))

class TestTask3_2(unittest.TestCase):
    def setUp(self):
        self.filein = mock_open() #To define in every test case
        self.fileout = io.StringIO()
        self.filein_filename = '' #To define in every test case
        self.fileout_filename = '' #To define in every test case

    def mock_open(self, filename, mode='r', *args, **kwargs):
        # Ignore args and kwargs
        if re.match(fr"(.*/)?{self.filein_filename}", filename):
            return self.filein()
        elif re.match(fr"(.*/)?{self.fileout_filename}", filename):
            if 'w' in mode:
                del self.fileout
                self.fileout = io.StringIO()
            return NoMoreClosingFunction(self.fileout)
        else:
            raise FileNotFoundError

    def test_with_default_file(self):
        "Test task 3.2 with default input file"
        self.filein_filename = "TASK3FILE.txt"
        self.fileout_filename = "FILE.TXT"
        with open(resource_directory / self.filein_filename) as f:
            filein_data = f.read()
            self.filein = mock_open(read_data=filein_data)
        with patch('builtins.open', side_effect=self.mock_open), patch('sys.stdout'):
            counter = task3_2(self.filein_filename, self.fileout_filename, 700)
        self.fileout.seek(0)
        try:
            data = [float(n) for n in self.fileout]
        except ValueError:
            self.fail("Non-float found in sample or invalid file structure")
        self.assertEqual(len(data), len(set(data)), msg="Repeat elements found in sample")
        avg = fmean(data)
        self.assertEqual(counter, len(list(filter(lambda a: float(a) < avg, filein_data.splitlines()))))

class TestTask3_3(unittest.TestCase):
    def setUp(self):
        self.filein = mock_open()
        self.fileout_notlower = io.StringIO()
        self.fileout_lower = io.StringIO()
        self.alpha = 5000
        self.no_of_sample = 700
    
    def mock_open(self, filename, mode='r', *args, **kwargs):
        if re.match(r"(.*/)?TASK3FILE.txt", filename):
            return self.filein()
        elif re.match(r"(.*/)?LOWER.TXT", filename):
            if 'w' in mode:
                del self.fileout_lower
                self.fileout_lower = io.StringIO()
            return NoMoreClosingFunction(self.fileout_lower)
        elif re.match(r"(.*/)NOTLOWER.TXT", filename):
            if 'w' in mode:
                del self.fileout_notlower
                self.fileout_notlower = io.StringIO()
            return NoMoreClosingFunction(self.fileout_notlower)
        else:
            raise FileNotFoundError(filename)
    
    def test_with_default(self):
        no_sample, alpha = 700, 5000
        with open(resource_directory / "TASK3FILE.txt") as f:
            filein_data = f.read()
            self.filein = mock_open(read_data=filein_data)
        with patch('builtins.open', side_effect=self.mock_open), patch("sys.stdout"):
            task3_3(self.no_of_sample, self.alpha)
        lower, notlower = self.fileout_lower.getvalue(), self.fileout_notlower.getvalue()
        self.assertTrue(lower and notlower, msg="LOWER.TXT and NOTLOWER.TXT cannot be empty")
        try:
            lower = [float(n.rstrip()) for n in lower.rstrip().splitlines()]
            notlower = [float(n.rstrip()) for n in notlower.rstrip().splitlines()]
        except ValueError:
            self.fail("Non-float found in sample or invalid file structure")
        self.assertEqual(len(lower), no_sample, "Incorrect number of samples in LOWER.TXT")
        self.assertEqual(len(notlower), no_sample, "Incorrect number of samples in NOTLOWER.TXT")
        lower_avg, notlower_avg = fmean(lower), fmean(notlower)
        self.assertLess(
            len(list(filter(lambda a: float(a) < lower_avg, filein_data.splitlines()))), 
            alpha, 
            "LOWER.TXT is not lower-sufficient"
        )
        self.assertGreater(
            len(list(filter(lambda a: float(a) < notlower_avg, filein_data.splitlines()))), 
            alpha, 
            "NOTLOWER.TXT is not lower-insufficient"
        )