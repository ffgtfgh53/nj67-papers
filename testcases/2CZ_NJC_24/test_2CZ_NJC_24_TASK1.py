import io
from pathlib import Path
import re
import string
import unittest
from unittest.mock import mock_open

from python_testcase_functions import NoMoreClosingFunction, load_user_functions


def task1_1_ans(c:str, n:int):
    if c == ' ': return '!'
    if not c.isalpha(): return -1
    res = ((ord(c) & 0b11111 )+ n) % 26 or 26
    return chr(res + 64) if c.isupper() else chr(res + 96)

class TestTask1_1(unittest.TestCase):
    def setUp(self):
        # TODO: Replace
        self._funcs = load_user_functions('\n'.join(Path(__file__).with_name('outfile_1.py').read_text().split('\n')[:43])) # To replace when actual string of code given
        self.func = self._funcs['task1_1']

    longMessage = False
    def test_all_c_n(self):
        "Test task 1.1 with all valid values of 'c' and 'n'"
        for n in range(1, 27):
            for c in string.ascii_letters:
                with self.subTest(n=n, c=c):
                    self.assertEqual(self.func(c, n), task1_1_ans(c, n))
    def test_special_chars(self):
        "Test task 1.1 with space and invalid characters"
        for i in "!@#$%^&*()~`-=+_1234567890[]}{;',./?><}😂\x98 ":
            with self.subTest(c=i):
                self.assertEqual(self.func(i, 12), task1_1_ans(i, 23))

class TestTask1_2(unittest.TestCase):
    longMessage = False
    def setUp(self):
        #Input to be overridden in each test case
        self.input = mock_open()
        self.output_buffer = io.StringIO()
        # TODO: Replace
        self._funcs = load_user_functions(
            '\n'.join(Path(__file__).with_name('outfile_1.py').read_text().split('\n')[:]),
            custom_globals={'open': self.mock_open}) # To replace when actual string of code given
        self.func = self._funcs['task1_2']

    
    def mock_open(self, filename, mode='r', *args, **kwargs):
        if re.match(r"(.*/)?TASK1DATA.txt", filename):
            return self.input.return_value
        elif 'w' in mode:
            # Write mode overwrites file, similarly this overwrites self.output_buffer
            del self.output_buffer
            self.output_buffer = io.StringIO()
            return NoMoreClosingFunction(self.output_buffer)
        elif 'a' in mode:
            return NoMoreClosingFunction(self.output_buffer)
        else:
            raise FileNotFoundError

    def test_default_use(self):
        """Test task 1.2 with the file given"""
        self.input = mock_open(read_data="This is my secret message# that I &need to encrypt@")
        self.func()
        self.assertEqual(self.output_buffer.getvalue().rstrip(), "Hrlg!lg!pm!vsmusd!aovgkjs#!hrdh!L!&qsog!dr!oqqbbdd@")

    def test_other_strings(self):
        "Test task 1.2 with another file of random characters"
        self.input = mock_open(read_data=";L]xF=5qQYo$Ba6]OLJ]}M(Cu^P=KF~1*O,6rE!d6< }UqN))tqt2F0aTL%Ip-dk+np7{}h$cR\\<sdL|p]_HtJT\"v&ve'y _.q#E")
        self.func()
        self.assertEqual(self.output_buffer.getvalue().rstrip(), ";V]lP=5aTMy$Pk6]YOX]}A(Fi^S=UI~1*C,6fO!r6<!}XeX))dth2I0kWZ%Ld-gy+qd7{}r$qB\\<cgZ|s]_KhTW\"f&jo'm!_.a#S")
    
    def test_print_file_content(self):
        """\
        Test task 1.2 outputs content of file it writes
        """
        self.input = mock_open(read_data="This is my secret message# that I &need to encrypt@")
        result = self.func()
        self.assertIn(self.output_buffer.getvalue().rstrip(), result.rstrip())