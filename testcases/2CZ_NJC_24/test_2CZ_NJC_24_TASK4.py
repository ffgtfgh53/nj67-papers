import re
import sqlite3
import unittest
from unittest.mock import patch
from random import randint
from itertools import cycle

from python_testcase_functions import NoMoreClosingFunction

from .outfile_4 import task4_1, Person, Player, Staff

class TestTask4_1(unittest.TestCase):
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

class TestTask4_2(unittest.TestCase):
    def test_class_inheritance(self):
        self.assertIn(Person, Player.mro(), "Player must inherit from Person")
        self.assertIn(Person, Staff.mro(), "Staff must inherit from Person")

    def test_class_person(self):
        testcases = [
            ({"full_name": "Bira Dawn", "date_of_birth": "1985-10-02"}, "BiraDawn1002"),
            ({"full_name": "George Robinson Jr.", "date_of_birth": "7654-03-21"}, "GeorgeRobinsonJr0321"),
            ({"full_name": "Harrison Ford", "date_of_birth": "1942-07-13"}, "HarrisonFord0713"),
            ({"full_name": "Mr. Bean", "date_of_birth": "1990-01-01"}, "MrBean0101"),
            ({"full_name": "...........", "date_of_birth": "0000-00-00"}, "0000"),
            ({"full_name": "", "date_of_birth": "0000-11-22"}, "1122"),
            ({"full_name": "X!@#n.o,?P;':y\"`-t", "date_of_birth": "0101-01-01"}, "XnoPyt0101")
        ]
        for kwargs, ans in testcases:
            with self.subTest("Test Person with arguments", **kwargs):
                try:
                    p = Person(**kwargs)
                except TypeError:
                    self.fail("Person.__init__() should accept correct keyword argumnets")
                self.assertEqual(p.is_player(), 'Maybe')
                self.assertEqual(p.is_staff(), 'Maybe')
                self.assertEqual(p.event_name(), ans)
    
    def test_class_player(self):
        testcases = [
            ({"full_name": "Bira Dawn", "date_of_birth": "1985-10-02", "char_name": "Rogerbrown", "team_name": "Echo"}, "Rogerbrown <Echo>"),
            ({"full_name": "George Robinson Jr.", "date_of_birth": "7654-03-21", "char_name": "wow look!", "team_name": "hehe i do cp"}, "wow look! <hehe i do cp>"),
            ({"full_name": "Harrison Ford", "date_of_birth": "1942-07-13", "char_name": "Ford does it best", "team_name": "Automobile supremacy"}, "Ford does it best <Automobile supremacy>"),
            ({"full_name": "Mr. Bean", "date_of_birth": "1990-01-01", "char_name": "Mr. Bean", "team_name": "no1 jokers"}, "Mr. Bean <no1 jokers>"),
            ({"full_name": "...........", "date_of_birth": "0000-00-00", "char_name": " ", "team_name": " "}, "  < >"),
            ({"full_name": "", "date_of_birth": "0000-11-22", "char_name": '', "team_name": ''}, " <>"),
            ({"full_name": "X!@#n.o,?P;':y\"`-t", "date_of_birth": "0101-01-01", "char_name": '123!@#', "team_name": "098)(*)"}, "123!@# <098)(*)>")
        ]
        for kwargs, ans in testcases:
            score = randint(0, 5000)
            with self.subTest("Test Player with arguments", score=score, **kwargs):
                try:
                    p = Player(**kwargs, score=score)
                except ValueError:
                    self.fail("Person.__init__() should accept correct keyword arguments")
                self.assertIsInstance(p.is_player(), bool, "is_player() should return a boolean")
                self.assertTrue(p.is_player(), "is_player() should return True")
                self.assertEqual(p.event_name(), ans, "Incorrect return value of event_name()")
    
    def test_class_staff(self):
        testcases = [
            ({"full_name": "Bira Dawn", "date_of_birth": "1985-10-02"}, "BiraDawn1002"),
            ({"full_name": "George Robinson Jr.", "date_of_birth": "7654-03-21"}, "GeorgeRobinsonJr0321"),
            ({"full_name": "Harrison Ford", "date_of_birth": "1942-07-13"}, "HarrisonFord0713"),
            ({"full_name": "Mr. Bean", "date_of_birth": "1990-01-01"}, "MrBean0101"),
            ({"full_name": "...........", "date_of_birth": "0000-00-00"}, "0000"),
            ({"full_name": "", "date_of_birth": "0000-11-22"}, "1122"),
            ({"full_name": "X!@#n.o,?P;':y\"`-t", "date_of_birth": "0101-01-01"}, "XnoPyt0101")
        ]
        for kwargs, ans in testcases:
            with self.subTest("Test staff with argumants", **kwargs):
                try:
                    s = Staff(**kwargs)
                except ValueError:
                    self.fail("Staff.__init__() should accept correct keyword arguments")
                self.assertIsInstance(s.is_staff(), bool, "is_staff() should return a boolean")
                self.assertTrue(s.is_staff(), "is_staff() should return True")
                self.assertTrue(s.event_name().startswith(ans), "event_name() must start with Player.event_name")
                self.assertTrue(s.event_name().endswith('Staff'), "event_name() must end with 'Staff'")
                self.assertLessEqual(len(s.event_name()), len(ans)+6, "event_name() too long")