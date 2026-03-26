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
        stripped = [i for i in name if i not in (string.punctuation and " ")]
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
    

# Task 4.3
import sqlite3
import csv

Event_People = []

with open("./Resources/TASK4/TASK4PEOPLE.CSV") as file:
    reader = csv.reader(file)
    data = [i for i in reader if i[-1] != "Player"]

for i in data:
    if i[-1] == "Person":
        temp = Person(i[0],i[1])
    else:
        temp = Staff(i[0],i[1])
    Event_People.append(temp)



with open("./Resources/TASK4/TASK4PLAYERS.CSV") as file:
    reader = csv.reader(file)
    players = list(reader)

for i in players:
    temp = Player(*i)
    Event_People.append(temp)

bool_dict = {
    "Player":[1,0],
    "Staff":[0,1],
    "Person":[0,0]
}

conn = sqlite3.connect("./Resources/TASK4/esports.db")
for indiv in Event_People:
    if isinstance(indiv,Staff):
        bool_list = bool_dict["Staff"]
        values = tuple([indiv.full_name,indiv.date_of_birth]+bool_list)
        query = "INSERT INTO PEOPLE (FullName,DateofBirth,IsPlayer,IsStaff) VALUES (?,?,?,?)"
        conn.execute(query,values)
    elif isinstance(indiv,Player):
        bool_list = bool_dict["Player"]
        values_people = tuple([indiv.full_name,indiv.date_of_birth]+bool_list)
        values_player = tuple([indiv.team_name,indiv.char_name,indiv.event_name(),indiv.score,indiv.full_name])
        queries = [["INSERT INTO PEOPLE (FullName,DateofBirth,IsPlayer,IsStaff) VALUES (?,?,?,?)",values_people],["INSERT INTO PLAYER (PersonID,TeamName,CharacterName,EventName,Score) SELECT p.PersonID,?,?,?,? from PEOPLE p WHERE p.FullName = ? ",values_player]]
        for query in queries:
            conn.execute(*query)
    elif isinstance(indiv,Person):
        bool_list = bool_dict["Person"]
        values = tuple([indiv.full_name,indiv.date_of_birth]+bool_list)
        query = "INSERT INTO PEOPLE (FullName,DateofBirth,IsPlayer,IsStaff) VALUES (?,?,?,?)"
        conn.execute(query,values)
conn.commit()
conn.close()


    