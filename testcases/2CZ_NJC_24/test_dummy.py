from typing import TYPE_CHECKING
import unittest

from RestrictedPython import compile_restricted

if TYPE_CHECKING:
    from .outfile_test import task_malicous_imports

exec(compile_restricted("from .outfile_test import task_malicous_imports"))

class TestSecurity(unittest.TestCase):
    def test_imports(self):
        exec(compile_restricted("task_malicous_imports(self)"))

class TestTaskCrocodile(unittest.TestCase):
    def testFailure(self):
        self.fail("This message will and should always appear as a failure, safe to ignore")