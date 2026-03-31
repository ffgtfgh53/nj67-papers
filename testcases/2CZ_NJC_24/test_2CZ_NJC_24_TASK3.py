import csv
import io
import unittest
import random
import re
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
from statistics import fmean, mean

from python_testcase_functions import NoMoreClosingFunction

resource_directory = Path(__file__).parent / 'Resources'

from outfile_3 import task3_1

def task3_1_ans(values: list[int]):
    l = len(values)
    if l <= 1:
        return values
    def merge_helper(a, b):
        res = []
        while a and b:
            if a[0] < b[0]:
                res.append(a.pop(0))
            else:
                res.append(b.pop(0))
        res.extend(a + b)
        return res
    return merge_helper(task3_1(values[:l//2]), task3_1(values[l//2:]))

class TestTask1(unittest.TestCase):
    def test_sort(self):
        "Test task 3.1 with random 100 random integers"
        arr = random.choices(range(1000), k=100)
        with patch('sys.stdout'):
            self.assertEqual(task3_1(arr), task3_1_ans(arr))

from outfile_3 import task3_2

class TestTask2(unittest.TestCase):
    def setUp(self):
        self.filein = mock_open() #To define in every test case
        self.fileout = io.StringIO()
        self.filein_filename = '' #To define in every test case
        self.fileout_filename = '' #To define in every test case

    def mock_open(self, filename, mode='r', *args, **kwargs):
        if re.match(fr"(.*/)?{self.filein_filename}", filename):
            return self.filein.return_value
        elif re.match(fr"(.*/)?{self.fileout_filename}", filename):
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
        with patch('builtins.open', side_effect=self.mock_open):
            counter = task3_2(self.filein_filename, self.fileout_filename, 700)
        data = []
        self.fileout.seek(0)
        data = [float(n) for n in self.fileout]
        avg = fmean(data)
        counter2 = 0
        for i in filein_data.splitlines():
            if float(i) < avg:
                counter2 += 1
        self.assertEqual(counter, len(list(filter(lambda a: float(a) < avg, filein_data.splitlines()))))