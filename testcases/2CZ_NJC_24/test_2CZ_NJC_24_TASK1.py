import io
import re
import unittest, unittest.mock
import string

class NoMoreClosingFunction():
    "Wrapper which turns obj.close to lambda and hides object behind ._obj"
    def __init__(self, obj):
        self._obj = obj
    
    def __getattr__(self, name):
        if name == 'close':
            return lambda: None
        return getattr(self._obj, name)
    def __enter__(self, *args, **kwargs):
        "Dont check what file is opened, take everything"
        return self._obj.__enter__()
    def __exit__(self, *args, **kwargs):
        pass

from .outfile import task1_1
def task1_1_ans(c:str, n:int):
    if c == ' ': return '!'
    if not c.isalpha(): return -1
    res = ((ord(c) & 0b11111 )+ n) % 26 or 26
    return chr(res + 64) if c.isupper() else chr(res + 96)

class TestTask1(unittest.TestCase):
    def test_all_c_n(self):
        "Test all valid values of 'c' and 'n'"
        for n in range(1, 27):
            for c in string.ascii_letters:
                with self.subTest(n=n, c=c):
                    self.assertEqual(task1_1(c, n), task1_1_ans(c, n))
    def test_space(self):
        self.assertEqual(task1_1(' ', 13), '!')
    def test_special_chars(self):
        "Test using invalid characters"
        for i in "!@#$%^&*()~`-=+_1234567890[]}{;',./?><}😂\x98":
            with self.subTest(c=i):
                self.assertEqual(task1_1(i, 12), -1)

from .outfile import task1_2

class TestTask2(unittest.TestCase):
    def setUp(self):
        #Input to be overridden in each test case
        self.input = unittest.mock.mock_open()
        self.output_buffer = io.StringIO()
    
    def mock_open(self, filename, mode='r', *args, **kwargs):
        if re.match(r"(.*/)?TASK1DATA.txt", filename):
            return self.input.return_value
        elif 'w' in mode:
            return NoMoreClosingFunction(self.output_buffer)
        else:
            raise FileNotFoundError

    @unittest.mock.patch('builtins.open')
    def test_default_use(self, mock_file):
        mock_file.side_effect = self.mock_open
        self.input = unittest.mock.mock_open(read_data="This is my secret message# that I &need to encrypt@")
        task1_2()
        self.assertEqual(self.output_buffer.getvalue().rstrip(), "Hrlg!lg!pm!vsmusd!aovgkjs#!hrdh!L!&qsog!dr!oqqbbdd@")

    @unittest.mock.patch('builtins.open')
    def test_other_strings(self, mock_file):
        mock_file.side_effect = self.mock_open
        self.input = unittest.mock.mock_open(read_data=r""";L]xF=5qQYo"Ba6]OLJ]}M(Cu^P=KF~1*O,6rE!d6< }UqN))tqt2F0aTL%Ip-dk+np7{}h$cR\<sdL|p]_HtJT"v&ve'y _.q#E""")
        task1_2()
        self.assertEqual(self.output_buffer.getvalue().rstrip(), r""";V]lP=5aTMy"Pk6]YOX]}A(Fi^S=UI~1*C,6fO!r6<!}XeX))dth2I0kWZ%Ld-gy+qd7{}r$qB\<cgZ|s]_KhTW"f&jo'm!_.a#S""")
    

