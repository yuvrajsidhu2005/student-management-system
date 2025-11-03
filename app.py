from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_this_in_production'

DATABASE = 'student_management.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    total_students = conn.execute('SELECT COUNT(*) as count FROM Student').fetchone()['count']
    total_subjects = conn.execute('SELECT COUNT(*) as count FROM Subject').fetchone()['count']
    total_grades = conn.execute('SELECT COUNT(*) as count FROM Grade').fetchone()['count']
    attendance_stats = conn.execute('''
        SELECT COUNT(*) as total_records,
               SUM(CASE WHEN Status = 'Present' THEN 1 ELSE 0 END) as present_count,
               SUM(CASE WHEN Status = 'Absent' THEN 1 ELSE 0 END) as absent_count
        FROM Attendance
    ''').fetchone()
    average_marks = conn.execute('SELECT AVG(Marks) as avg FROM Grade').fetchone()['avg']
    average_marks = round(average_marks, 2) if average_marks else 0
    recent_students = conn.execute('SELECT * FROM Student ORDER BY StudentID DESC LIMIT 5').fetchall()
    top_performers = conn.execute('''
        SELECT Student.Name, AVG(Grade.Marks) as average
        FROM Student
        JOIN Grade ON Student.StudentID = Grade.StudentID
        GROUP BY Student.StudentID
        ORDER BY average DESC
        LIMIT 5
    ''').fetchall()
    conn.close()
    return render_template('dashboard.html', 
                         total_students=total_students,
                         total_subjects=total_subjects,
                         total_grades=total_grades,
                         attendance_stats=attendance_stats,
                         average_marks=average_marks,
                         recent_students=recent_students,
                         top_performers=top_performers)

@app.route('/students')
def students():
    search = request.args.get('search', '')
    conn = get_db_connection()
    if search:
        students = conn.execute('SELECT * FROM Student WHERE Name LIKE ? OR Email LIKE ? OR Course LIKE ?',
            (f'%{search}%', f'%{search}%', f'%{search}%')).fetchall()
    else:
        students = conn.execute('SELECT * FROM Student').fetchall()
    conn.close()
    return render_template('students.html', students=students, search=search)

@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']
        year = request.form['year']
        conn = get_db_connection()
        conn.execute('INSERT INTO Student (Name, Email, Course, Year) VALUES (?, ?, ?, ?)', (name, email, course, year))
        conn.commit()
        conn.close()
        flash('Student added successfully!', 'success')
        return redirect(url_for('students'))
    return render_template('add_student.html')

@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM Student WHERE StudentID = ?', (id,)).fetchone()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']
        year = request.form['year']
        conn.execute('UPDATE Student SET Name = ?, Email = ?, Course = ?, Year = ? WHERE StudentID = ?',
                    (name, email, course, year, id))
        conn.commit()
        conn.close()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('students'))
    conn.close()
    return render_template('edit_student.html', student=student)

@app.route('/students/delete/<int:id>')
def delete_student(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Student WHERE StudentID = ?', (id,))
    conn.commit()
    conn.close()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('students'))

@app.route('/subjects')
def subjects():
    search = request.args.get('search', '')
    conn = get_db_connection()
    if search:
        subjects = conn.execute('SELECT * FROM Subject WHERE SubjectName LIKE ? OR Course LIKE ?',
            (f'%{search}%', f'%{search}%')).fetchall()
    else:
        subjects = conn.execute('SELECT * FROM Subject').fetchall()
    conn.close()
    return render_template('subjects.html', subjects=subjects, search=search)

@app.route('/subjects/add', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        subject_name = request.form['subject_name']
        course = request.form['course']
        conn = get_db_connection()
        conn.execute('INSERT INTO Subject (SubjectName, Course) VALUES (?, ?)', (subject_name, course))
        conn.commit()
        conn.close()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('subjects'))
    return render_template('add_subject.html')

@app.route('/subjects/edit/<int:id>', methods=['GET', 'POST'])
def edit_subject(id):
    conn = get_db_connection()
    subject = conn.execute('SELECT * FROM Subject WHERE SubjectID = ?', (id,)).fetchone()
    if request.method == 'POST':
        subject_name = request.form['subject_name']
        course = request.form['course']
        conn.execute('UPDATE Subject SET SubjectName = ?, Course = ? WHERE SubjectID = ?', (subject_name, course, id))
        conn.commit()
        conn.close()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('subjects'))
    conn.close()
    return render_template('edit_subject.html', subject=subject)

@app.route('/subjects/delete/<int:id>')
def delete_subject(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Subject WHERE SubjectID = ?', (id,))
    conn.commit()
    conn.close()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('subjects'))

@app.route('/grades')
def grades():
    search = request.args.get('search', '')
    conn = get_db_connection()
    if search:
        grades = conn.execute('''
            SELECT Grade.*, Student.Name as StudentName, Subject.SubjectName 
            FROM Grade 
            JOIN Student ON Grade.StudentID = Student.StudentID 
            JOIN Subject ON Grade.SubjectID = Subject.SubjectID
            WHERE Student.Name LIKE ? OR Subject.SubjectName LIKE ?
        ''', (f'%{search}%', f'%{search}%')).fetchall()
    else:
        grades = conn.execute('''
            SELECT Grade.*, Student.Name as StudentName, Subject.SubjectName 
            FROM Grade 
            JOIN Student ON Grade.StudentID = Student.StudentID 
            JOIN Subject ON Grade.SubjectID = Subject.SubjectID
        ''').fetchall()
    conn.close()
    return render_template('grades.html', grades=grades, search=search)

@app.route('/grades/add', methods=['GET', 'POST'])
def add_grade():
    conn = get_db_connection()
    if request.method == 'POST':
        student_id = request.form['student_id']
        subject_id = request.form['subject_id']
        marks = request.form['marks']
        conn.execute('INSERT INTO Grade (StudentID, SubjectID, Marks) VALUES (?, ?, ?)', (student_id, subject_id, marks))
        conn.commit()
        conn.close()
        flash('Grade added successfully!', 'success')
        return redirect(url_for('grades'))
    students = conn.execute('SELECT * FROM Student').fetchall()
    subjects = conn.execute('SELECT * FROM Subject').fetchall()
    conn.close()
    return render_template('add_grade.html', students=students, subjects=subjects)

@app.route('/grades/edit/<int:id>', methods=['GET', 'POST'])
def edit_grade(id):
    conn = get_db_connection()
    grade = conn.execute('SELECT * FROM Grade WHERE GradeID = ?', (id,)).fetchone()
    if request.method == 'POST':
        student_id = request.form['student_id']
        subject_id = request.form['subject_id']
        marks = request.form['marks']
        conn.execute('UPDATE Grade SET StudentID = ?, SubjectID = ?, Marks = ? WHERE GradeID = ?',
                    (student_id, subject_id, marks, id))
        conn.commit()
        conn.close()
        flash('Grade updated successfully!', 'success')
        return redirect(url_for('grades'))
    students = conn.execute('SELECT * FROM Student').fetchall()
    subjects = conn.execute('SELECT * FROM Subject').fetchall()
    conn.close()
    return render_template('edit_grade.html', grade=grade, students=students, subjects=subjects)

@app.route('/grades/delete/<int:id>')
def delete_grade(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Grade WHERE GradeID = ?', (id,))
    conn.commit()
    conn.close()
    flash('Grade deleted successfully!', 'success')
    return redirect(url_for('grades'))

@app.route('/attendance')
def attendance():
    search = request.args.get('search', '')
    conn = get_db_connection()
    if search:
        attendance = conn.execute('''
            SELECT Attendance.*, Student.Name as StudentName 
            FROM Attendance 
            JOIN Student ON Attendance.StudentID = Student.StudentID
            WHERE Student.Name LIKE ? OR Attendance.Date LIKE ?
        ''', (f'%{search}%', f'%{search}%')).fetchall()
    else:
        attendance = conn.execute('''
            SELECT Attendance.*, Student.Name as StudentName 
            FROM Attendance 
            JOIN Student ON Attendance.StudentID = Student.StudentID
        ''').fetchall()
    conn.close()
    return render_template('attendance.html', attendance=attendance, search=search)

@app.route('/attendance/add', methods=['GET', 'POST'])
def add_attendance():
    conn = get_db_connection()
    if request.method == 'POST':
        student_id = request.form['student_id']
        date = request.form['date']
        status = request.form['status']
        conn.execute('INSERT INTO Attendance (StudentID, Date, Status) VALUES (?, ?, ?)', (student_id, date, status))
        conn.commit()
        conn.close()
        flash('Attendance marked successfully!', 'success')
        return redirect(url_for('attendance'))
    students = conn.execute('SELECT * FROM Student').fetchall()
    conn.close()
    return render_template('add_attendance.html', students=students)

@app.route('/attendance/edit/<int:id>', methods=['GET', 'POST'])
def edit_attendance(id):
    conn = get_db_connection()
    attendance = conn.execute('SELECT * FROM Attendance WHERE AttendanceID = ?', (id,)).fetchone()
    if request.method == 'POST':
        student_id = request.form['student_id']
        date = request.form['date']
        status = request.form['status']
        conn.execute('UPDATE Attendance SET StudentID = ?, Date = ?, Status = ? WHERE AttendanceID = ?',
                    (student_id, date, status, id))
        conn.commit()
        conn.close()
        flash('Attendance updated successfully!', 'success')
        return redirect(url_for('attendance'))
    students = conn.execute('SELECT * FROM Student').fetchall()
    conn.close()
    return render_template('edit_attendance.html', attendance=attendance, students=students)

@app.route('/attendance/delete/<int:id>')
def delete_attendance(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Attendance WHERE AttendanceID = ?', (id,))
    conn.commit()
    conn.close()
    flash('Attendance record deleted successfully!', 'success')
    return redirect(url_for('attendance'))

@app.route('/report-cards')
def report_cards():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM Student').fetchall()
    report_data = []
    for student in students:
        grades = conn.execute('''
            SELECT Subject.SubjectName, Grade.Marks 
            FROM Grade 
            JOIN Subject ON Grade.SubjectID = Subject.SubjectID 
            WHERE Grade.StudentID = ?
        ''', (student['StudentID'],)).fetchall()
        attendance = conn.execute('''
            SELECT COUNT(*) as total, SUM(CASE WHEN Status = 'Present' THEN 1 ELSE 0 END) as present
            FROM Attendance WHERE StudentID = ?
        ''', (student['StudentID'],)).fetchone()
        total_marks = sum([g['Marks'] for g in grades]) if grades else 0
        total_subjects = len(grades)
        average = total_marks / total_subjects if total_subjects > 0 else 0
        attendance_total = attendance['total'] if attendance['total'] else 0
        attendance_present = attendance['present'] if attendance['present'] else 0
        attendance_percentage = (attendance_present / attendance_total * 100) if attendance_total > 0 else 0
        if average >= 90:
            grade = 'A+'
        elif average >= 80:
            grade = 'A'
        elif average >= 70:
            grade = 'B'
        elif average >= 60:
            grade = 'C'
        elif average >= 50:
            grade = 'D'
        else:
            grade = 'F'
        report_data.append({
            'student': student,
            'grades': grades,
            'total_marks': total_marks,
            'average': round(average, 2),
            'grade': grade,
            'attendance_percentage': round(attendance_percentage, 2),
            'attendance_total': attendance_total,
            'attendance_present': attendance_present
        })
    conn.close()
    return render_template('report_cards.html', report_data=report_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
