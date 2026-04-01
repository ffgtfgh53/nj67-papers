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