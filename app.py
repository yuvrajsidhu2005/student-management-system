from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('student_management.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Students page - View all students
@app.route('/students')
def students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM Student ORDER BY StudentID').fetchall()
    conn.close()
    return render_template('students.html', students=students)

# Add new student
@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    email = request.form['email']
    course = request.form['course']
    year = request.form['year']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO Student (Name, Email, Course, Year) VALUES (?, ?, ?, ?)',
                 (name, email, course, year))
    conn.commit()
    conn.close()
    flash('Student added successfully!', 'success')
    return redirect(url_for('students'))

# Subjects page
@app.route('/subjects')
def subjects():
    conn = get_db_connection()
    subjects = conn.execute('SELECT * FROM Subject ORDER BY SubjectID').fetchall()
    conn.close()
    return render_template('subjects.html', subjects=subjects)

# Grades page
@app.route('/grades')
def grades():
    conn = get_db_connection()
    grades = conn.execute('''
        SELECT Grade.GradeID, Student.Name, Subject.SubjectName, Grade.Marks
        FROM Grade
        JOIN Student ON Grade.StudentID = Student.StudentID
        JOIN Subject ON Grade.SubjectID = Subject.SubjectID
        ORDER BY Grade.GradeID
    ''').fetchall()
    conn.close()
    return render_template('grades.html', grades=grades)

# Attendance page
@app.route('/attendance')
def attendance():
    conn = get_db_connection()
    attendance = conn.execute('''
        SELECT Attendance.AttendanceID, Student.Name, Attendance.Date, Attendance.Status
        FROM Attendance
        JOIN Student ON Attendance.StudentID = Student.StudentID
        ORDER BY Attendance.Date DESC
    ''').fetchall()
    conn.close()
    return render_template('attendance.html', attendance=attendance)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

