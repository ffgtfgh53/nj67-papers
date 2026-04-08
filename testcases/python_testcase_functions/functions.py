from __future__ import annotations # python 3.8 support

import io
import sqlite3
import unittest

from typing import Any

class NoMoreClosingFunction():
    """
    Wrapper around io.StringIO which removes .close() and .__exit__() methods

    Useful for returning a StringIO to a patched function which we can access later after function exits
    """
    def __init__(self, obj: Any=io.StringIO):
        self._obj = obj
    
    def __getattr__(self, name):
        if name == 'close':
            return lambda: None
        return getattr(self._obj, name)
    def __enter__(self, *args, **kwargs):
        # Don't check arguments of open(), they should have been check in self.mock_open()
        return self._obj.__enter__()
    def __exit__(self, exc_type, exc_value, traceback):
        pass

def sqlite3_verify_table(
        testcase: unittest.TestCase,
        conn: sqlite3.Connection,
        table_name: str,
        expected_table: dict[str, dict[str, dict[str, str]]]):
    table = conn.execute(f"PRAGMA table_info({table_name})")
    table_fk = conn.execute(f"PRAGMA foreign_key_list({table_name})")
    with testcase.subTest(f"Verify types of each column in {table_name}"):
        sqlite3_verify_column_type(testcase, table, expected_table)
    with testcase.subTest(f"Verify foreign keys in {table_name}"):
        sqlite3_verify_foreign_key(testcase, table_fk, expected_table)        

def sqlite3_verify_column_type(
        testcase: unittest.TestCase, 
        table: sqlite3.Cursor, 
        expected: dict[str, dict[str, dict]]):
    no_row = 0
    for _, col_name, col_type, _, _, col_pk in table:
        try:
            testcase.assertEqual(expected['cols'][col_name]['type'], col_type.upper())
            if expected['cols'][col_name].get('pk', False):
                testcase.assertTrue(col_pk, f"{col_name} is not primary key")
            no_row += 1
        except KeyError:
            testcase.fail(f"Unknown or extra column {col_name}")
    testcase.assertEqual(len(expected['cols']), no_row, "Missing column(s)")

def sqlite3_verify_foreign_key(
        testcase: unittest.TestCase, 
        table: sqlite3.Cursor, 
        expected: dict[str, dict[str, dict]]):
    no_fk = 0
    for _, _, org_table_name, org_name, curr_name, _, _, _ in table:
        try:
            testcase.assertEqual((org_table_name, org_name),
                (expected['fk'][curr_name]['ref_table'], expected['fk'][curr_name]['ref_col']),
                "Foreign key mismatch")
            no_fk += 1
        except KeyError:
            testcase.fail(f"Unknown or extra foreign key {curr_name}")
    testcase.assertEqual(len(expected['fk']), no_fk, "Missing foreign key(s)")
