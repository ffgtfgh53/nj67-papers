# type: ignore 
# (disables linters such as pyright)
def task4_1():
    #  Task 4.1

    import sqlite3

    # CREATE esports.db

    tables_sql = [
        """CREATE TABLE IF NOT EXISTS PEOPLE(
            PersonID INTEGER PRIMARY KEY AUTOINCREMENT,
            FullName TEXT,
            DateOfBirth TEXT,
            IsPlayer INTEGER CHECK (IsPlayer in (0,1)),
            IsStaff INTEGER CHECK (IsStaff in (0,1))
        )""",
        """CREATE TABLE IF NOT EXISTS PLAYER(
            PersonID INTEGER,
            TeamName TEXT,
            CharacterName TEXT,
            EventName TEXT,
            Score INTEGER,
            PRIMARY KEY (PersonID, TeamName),
            FOREIGN KEY (PersonID) REFERENCES PEOPLE(PersonID)
        )"""
    ]

    conn = sqlite3.connect("./Resources/TASK4/esports.db")
    for query in tables_sql:
        conn.execute(query)
    conn.commit()
    conn.close()

# Task 4.2
import string

class Person:
    def __init__(self,full_name,date_of_birth):
        self.full_name = full_name
        self.date_of_birth = date_of_birth
    def is_player(self):
        return "Maybe"
    def is_staff(self):
        return "Maybe"
    def event_name(self):
        name = self.full_name
        dob = self.date_of_birth
        stripped = [i for i in name if i not in (string.punctuation + " ")]
        y,m,d = dob.split("-")
        stripped += [m,d]
        event_name = "".join(stripped)
        return event_name
    

class Player(Person):
    def __init__(self,full_name,date_of_birth,team_name,char_name,score):
        super().__init__(full_name,date_of_birth)
        self.char_name = char_name
        self.team_name = team_name
        self.score = score
    def event_name(self):
        char_name = self.char_name
        team_name = self.team_name
        event_name = f"{char_name} <{team_name}>"
        return event_name
    def is_player(self):
        return True 
    
class Staff(Person):
    def __init__(self,full_name,date_of_birth):
        super().__init__(full_name,date_of_birth)
    def is_staff(self):
        return True
    def event_name(self):
        p_event_name = super().event_name()
        event_name = p_event_name + "Staff"
        return event_name