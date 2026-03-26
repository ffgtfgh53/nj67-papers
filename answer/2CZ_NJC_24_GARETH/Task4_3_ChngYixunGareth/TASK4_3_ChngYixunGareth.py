# Task 4.4
import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    conn = sqlite3.connect("../Resources/TASK4/esports.db")
    cursor = conn.execute("SELECT p.TeamName,p.CharacterName,p.EventName,p.Score FROM PLAYER p ORDER BY p.TeamName,p.Score DESC")
    data = cursor.fetchall()
    conn.close()
    teams = set([i[0] for i in data])
    return render_template("index.html",dataset=teams)

@app.route('/<TeamName>')
def teaminfo(TeamName):
    conn = sqlite3.connect("../Resources/TASK4/esports.db")
    cursor = conn.execute("SELECT p.TeamName,p.CharacterName,p.EventName,p.Score FROM PLAYER p ORDER BY p.TeamName,p.Score DESC")
    data = cursor.fetchall()
    conn.close()
    team_info = [i for i in data if i[0] == TeamName]
    return render_template("team.html",dataset = team_info)


if __name__ == "__main__":
    app.run(debug=True)
