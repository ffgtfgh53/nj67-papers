from flask import Flask, render_template, url_for
import sqlite3

app = Flask(__name__) 

def get_teams():
    conn = sqlite3.connect("../esports.db")
    cursor = conn.cursor()
    cursor.execute("SELECT TeamName, CharacterName, EventName, Score FROM player")
    return cursor.fetchall()
    conn.commit()
    conn.disconnect()

@app.route('/')
def home():
    data = get_teams()
    teams = []
    for record in data:
        if record[0] not in teams:
            teams.append(record[0])
    print(teams)
    return render_template('index.html', teams=teams)

@app.route('/<teamname>')
def team(teamname):
    teams = get_teams()
    teamdata = [t for t in teams if t[0] == teamname]
    return render_template('team.html', teamdata=teamdata)
    
if __name__ == "__main__":
    app.run(debug=True)

