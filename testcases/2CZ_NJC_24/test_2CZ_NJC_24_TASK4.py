import re
import sqlite3
import unittest
from unittest.mock import patch
from random import randint

from python_testcase_functions import NoMoreClosingFunction, sqlite3_verify_table

from .outfile_4 import task4_1, Person, Player, Staff

class TestTask4_1(unittest.TestCase):
    longMessage = False
    def setUp(self):
        self.database_conn = sqlite3.connect(":memory:")
        with patch('sqlite3.connect', side_effect=self.mock_connect):
            task4_1("esports.db")

    def mock_connect(self, database, *args, **kwargs):
        if re.match(r"(.*/)?esports.db", str(database)):
            return NoMoreClosingFunction(self.database_conn)
        else:
            self.fail(f"Wrong filename {database}")
        
    def test_tables_exists(self):
        "Test task 4.1 has neccessary tables"
        tables = self.database_conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        self.assertIn(("PLAYER",), tables, "Player table missing from database")
        self.assertIn(("PEOPLE",), tables, "People table missing from database")
    
    def test_table_people(self):
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
        sqlite3_verify_table(self, self.database_conn, "PEOPLE", expected_people_table)

    def test_table_player(self):
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
        sqlite3_verify_table(self, self.database_conn, "PLAYER", expected_player_table)

class TestTask4_2(unittest.TestCase):
    longMessage = False
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