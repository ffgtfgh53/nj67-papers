def task_malicous_imports(self):
    try:
        import sqlite3
        import math
        import statistics
        import json
        import re
        self.assertEqual(math.sqrt(100), 10)
        self.assertEqual(set((1, 2, 3, 4, 5)), frozenset((5, 4, 3, 2, 1)))
    except Exception as e:
        self.fail(f"Error importing safe modules: {e}")
    try:
        import sys
        sys.stdout.write("hahaha\n")
    except:
        pass
    else:
        self.fail("No error when importing sys")
    try:
        import os
    except:
        pass
    else:
        self.fail("No error when importing os")