from flask import Flask, render_template, request, url_for, redirect
import sqlite3

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/choice', methods=['POST']) 
def choice():  
    # Retrieve the value of the 'choice' input field  
    user_choice = request.form.get('choice')

    if user_choice == '1':
        return redirect('/search')
    elif user_choice == '2':
        return redirect(url_for('staff_workload'))
    else:
        return render_template('home.html')

# Search for Appointment    
@app.route('/search', methods=['GET', 'POST'])
def search_appointment():  
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        appointment_date = request.form['appointment_date']
        conn = sqlite3.connect('../Resources/CLINIC.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT Appointment.AppointmentID, Patient.PatientID, Patient.Name, Staff.StaffID, Staff.Name, Appointment.AppointmentDate, Appointment.Diagnosis 
            FROM Appointment
            INNER JOIN Patient ON Appointment.PatientID = Patient.PatientID
            INNER JOIN Staff ON Appointment.StaffID = Staff.StaffID
            WHERE Patient.Name = ? AND Appointment.AppointmentDate = ?
        ''', (patient_name, appointment_date))
        appointments = cursor.fetchall()
        
        conn.close()
        if not appointments:
            return render_template('search.html', message="No appointments found")
        return render_template('search.html', appointments=appointments)
    return render_template('search.html')

# List Staff Workload
@app.route('/workload', methods=['GET'])
def staff_workload():  
    conn = sqlite3.connect('../Resources/CLINIC.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT Staff.Name, Staff.Role, COUNT(Appointment.AppointmentID) as AppointmentCount
        FROM Staff
        LEFT OUTER JOIN Appointment ON Staff.StaffID = Appointment.StaffID
        GROUP BY Staff.Name, Staff.Role
        ORDER BY AppointmentCount DESC
    ''')
    workload = cursor.fetchall()
    conn.close()
    return render_template('workload.html', workload=workload)

if __name__ == '__main__':
    app.run()