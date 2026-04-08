import unittest

from python_testcase_functions import SecureTest

@SecureTest(additional_modules=['sqlite3'])
class TestDummy(unittest.TestCase):
    def test_dummy(self):
        import sqlite3 # Ok
        import sys # PermissionError

@SecureTest()
class TestTaskCrocodile(unittest.TestCase):
    def testFailure(self):
        self.fail("Default failure with this message")

@SecureTest()
class TestTaskSkibidiSigma(unittest.TestCase):
    def testError(self):
        raise Exception("ERROR!!!")

    def testErrorERROR(self):
        with open("fauhwijsiwsj/dwedjoied") as f:
            pass

    def testExecError(self):
        exec("print(2)")
    
    def testImportError(self):
        import os
        print(os.listdir()) 

    def testNoImportError(self):
        import math
        self.assertEqual(math.sqrt(100), 10.)