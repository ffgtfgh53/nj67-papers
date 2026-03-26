# Task 4.4
from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/search')
def search():
    return render_template("search.html")

@app.route('/workload')
def workload():
    conn = sqlite3.connect("./Resources/TASK4/CLINIC.db")
    query ="""SELECT s.Name, s.Role, COUNT(a.AppointmentID) AS count FROM Appointment a JOIN Staff s ON a.staffID = s.StaffID GROUP BY s.Name,s.Role ORDER BY count DESC"""
    cursor = conn.execute(query)
    data = cursor.fetchall()
    conn.close()
    return render_template("workload.html",dataset=data)

@app.route('/query',methods=["POST"])
def query():
    if request.method == "POST":
        patient_name = request.form["Name"]
        date = request.form["Date"]
        print(request.form)
        try: 
            conn = sqlite3.connect("./Resources/TASK4/CLINIC.db")
            query = """SELECT a.AppointmentID, a.PatientID,p.Name,a.StaffID,s.Name,a.AppointmentDate,a.Diagnosis 
            from Appointment a 
            JOIN Patient p ON a.PatientID = p.PatientID 
            JOIN Staff s ON a.StaffID = s.StaffID
            WHERE p.Name = ? AND a.AppointmentDate = ?
            """
            cursor = conn.execute(query,(patient_name,date))
            data = cursor.fetchone()
            print(data)
            conn.close()
        except:
            data = ""

    return render_template("results.html",dataset = data)


if __name__ == "__main__":
    app.run(debug=True)