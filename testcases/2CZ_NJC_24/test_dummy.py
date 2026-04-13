import json
from pathlib import Path
import re
import sqlite3
import statistics
import textwrap
import unittest
from unittest.mock import call, patch

from python_testcase_functions import load_user_functions

class TestSecurity(unittest.TestCase):
    def setUp(self):
        try:
            self.funcs = load_user_functions(
                (Path(__file__).parent / "outfile_test.py").read_text(),
                extra_imports={'statistics': statistics, 'json': json, 're': re, 'sqlite3': sqlite3})
            self.func = self.funcs['task_malicous_imports']
        except RuntimeError as e:
            self.fail(f"Error importing user code: {e}")

    def test_imports(self):
        self.func(self)

class TestRestricted(unittest.TestCase):
    def test_default(self):
        user_code = textwrap.dedent('''
            def neighbour():
                print("Hey neighbour!")

            def task1_67():
                print("Hi from task1_67")
                neighbour()

            def task67_1():
                print("Hi from task67_1")
        ''')
        funcs = load_user_functions(user_code, ['task1_67'], block_print=False)
        with patch('sys.stdout') as mock_stdout:
            funcs['task1_67']() # Prints "Hi from task1_67" and "Hey neighbour!"
        mock_stdout.assert_has_calls([
            call.write('Hi from task1_67'),
            call.write('\n'),
            call.write('Hey neighbour!'),
            call.write('\n')
        ])

        with self.assertRaises(Exception):
            funcs['print']("Hello World!") # Fails


class TestTaskCrocodile(unittest.TestCase):
    def testFailure(self):
        self.fail("IGNORE: This message will and should always appear as a failure, safe to ignore")