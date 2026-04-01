from enum import verify
import re
import sqlite3
import unittest
from unittest.mock import mock_open, patch

from python_testcase_functions import NoMoreClosingFunction

from .outfile_4 import task4_1

class Testtask4_1(unittest.TestCase):
    def setUp(self):
        self.database_conn = sqlite3.connect(":memory:")
        with patch('sqlite3.connect', side_effect=self.mock_connect):
            task4_1()

    def mock_connect(self, database, *args, **kwargs):
        if re.match(r"(.*/)?esports.db", str(database)):
            return NoMoreClosingFunction(self.database_conn)
        else:
            self.fail(f"Wrong filename {database}")

    def verify_column_type(self, table: sqlite3.Cursor, expected: dict[str, dict[str, dict]]):
        no_row = 0
        for _, col_name, col_type, _, _, col_pk in table:
            try:
                self.assertEqual(expected['cols'][col_name]['type'], col_type.upper())
                if expected['cols'][col_name].get('pk', False):
                    self.assertTrue(col_pk, f"{col_name} is not primary key")
                no_row += 1
            except KeyError:
                self.fail(f"Unknown or extra column {col_name}")
        self.assertEqual(len(expected['cols']), no_row, "Missing column(s)")

    def verify_foreign_key(self, table: sqlite3.Cursor, expected: dict[str, dict[str, dict]]):
        no_fk = 0
        for _, _, org_table_name, org_name, curr_name, _, _, _ in table:
            try:
                self.assertEqual((org_table_name, org_name),
                    (expected['fk'][curr_name]['ref_table'], expected['fk'][curr_name]['ref_col']),
                    "Foreign key mismatch")
                no_fk += 1
            except KeyError:
                self.fail(f"Unknown or extra foreign key {curr_name}")
        self.assertEqual(len(expected['fk']), no_fk, "Missing foreign key(s)")

        
    def test_tables_exists(self):
        "Test task 4.1 has neccessary tables"
        tables = self.database_conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        self.assertIn(("PLAYER",), tables, "Player table missing from database")
        self.assertIn(("PEOPLE",), tables, "People table missing from database")
    
    def test_table_people(self):
        people = self.database_conn.execute("PRAGMA table_info(PEOPLE)")
        people_fk = self.database_conn.execute("PRAGMA foreign_key_list(PEOPLE)")
        expected_people_table = {
            'cols': {
                'PersonID': { 'type': 'INTEGER', 'pk': True},
                'FullName': { 'type': 'TEXT' },
                'DateOfBirth': { 'type': 'TEXT' },
                'IsPlayer': { 'type': 'INTEGER' },
                'IsStaff': { 'type': 'INTEGER'}
            },
            'fk': {}
        }
        with self.subTest("Verify types of each column in PEOPLE"):
            self.verify_column_type(people, expected_people_table)
        with self.subTest("Verify foreign keys in PEOPLE"):
            self.verify_foreign_key(people_fk, expected_people_table)        

    def test_table_player(self):
        player = self.database_conn.execute("PRAGMA table_info(PLAYER)")
        player_fk = self.database_conn.execute("PRAGMA foreign_key_list(PLAYER)")
        expected_player_table = {
            'cols': {
                'PersonID': { 'type': 'INTEGER', 'pk': True },
                'TeamName': { 'type': 'TEXT' },
                'CharacterName': { 'type': 'TEXT' },
                'EventName': { 'type': 'TEXT' },
                'Score': { 'type': 'INTEGER' }
            },
            'fk': {
                'PersonID': {
                    'ref_table': 'PEOPLE',
                    'ref_col': 'PersonID'
                }
            }
        }
        with self.subTest("Verify types of each column in PLAYER"):
            self.verify_column_type(player, expected_player_table)
        with self.subTest("Verify foreign keys in PLAYER"):
            self.verify_foreign_key(player_fk, expected_player_table)