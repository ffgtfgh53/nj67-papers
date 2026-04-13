import io
from pathlib import Path
import random
import re
from statistics import fmean
import unittest
from unittest.mock import mock_open

from python_testcase_functions import NoMoreClosingFunction, load_user_functions

resource_directory = Path(__file__).parent / 'Resources'

class TestTask3_1(unittest.TestCase):
    longMessage = False
    def setUp(self):
        # TODO: Replace
        self._funcs = load_user_functions('\n'.join(Path(__file__).with_name('outfile_3.py').read_text().split('\n')[:20])) # To replace when actual string of code given
        self.func = self.task3_1 = self._funcs['task3_1']

    def test_with_given(self):
        "Test task 3.1 with the case given"
        arr = [0,0,4,4,5,7,18,25,56,98]
        self.assertEqual(self.task3_1([56,25,4,98,0,18,4,5,7,0]), arr, "task3_1() does not match the condition given")
    def test_sort(self):
        "Test task 3.1 with random 100 random integers"
        arr = random.choices(range(1000), k=100)
        self.assertEqual(self.task3_1(arr), sorted(arr), "task3_1() does not properly sort randomly generated integers")

class TestTask3_2(unittest.TestCase):
    longMessage = False
    def setUp(self):
        self.filein = mock_open() #To define in every test case
        self.fileout = io.StringIO()
        self.filein_filename = '' #To define in every test case
        self.fileout_filename = '' #To define in every test case

        #TODO: replace
        import csv
        self._funcs = load_user_functions(
            '\n'.join(Path(__file__).with_name('outfile_3.py').read_text().split('\n')[35:59]),
            custom_globals={'open': self.mock_open},
            extra_imports={'csv': csv}
            ) # To replace when actual string of code given
        self.func = self.task3_1 = self._funcs['task3_2']


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
        counter = self.func(self.filein_filename, self.fileout_filename, 700)
        self.fileout.seek(0)
        try:
            data = [float(n) for n in self.fileout]
        except ValueError:
            self.fail("Non-float found in sample or invalid file structure")
        self.assertEqual(len(data), len(set(data)), msg="Repeat elements found in sample")
        avg = fmean(data)
        self.assertEqual(counter, len(list(filter(lambda a: float(a) < avg, filein_data.splitlines()))), "Counter value is incorrect based on output data")

class TestTask3_3(unittest.TestCase):
    longMessage = False
    def setUp(self):
        self.filein = mock_open()
        self.fileout_notlower = io.StringIO()
        self.fileout_lower = io.StringIO()
        self.alpha = 5000
        self.no_of_sample = 700

        #TODO: Replace
        import csv
        self._funcs = load_user_functions(
            '\n'.join(Path(__file__).with_name('outfile_3.py').read_text().split('\n')[59:]),
            custom_globals={'open': self.mock_open},
            extra_imports={'csv': csv}
            ) # To replace when actual string of code given
        self.func = self.task3_1 = self._funcs['task3_3']
    
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
        self.func(self.no_of_sample, self.alpha)
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