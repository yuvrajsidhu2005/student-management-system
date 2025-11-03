import sqlite3

def create_database():
    conn = sqlite3.connect('student_management.db')
    cursor = conn.cursor()
    
    # Create Student table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Student (
        StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Email TEXT UNIQUE,
        Course TEXT,
        Year INTEGER
    )
    ''')
    
    # Create Subject table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Subject (
        SubjectID INTEGER PRIMARY KEY AUTOINCREMENT,
        SubjectName TEXT NOT NULL,
        Course TEXT
    )
    ''')
    
    # Create Grade table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Grade (
        GradeID INTEGER PRIMARY KEY AUTOINCREMENT,
        StudentID INTEGER,
        SubjectID INTEGER,
        Marks INTEGER,
        FOREIGN KEY(StudentID) REFERENCES Student(StudentID),
        FOREIGN KEY(SubjectID) REFERENCES Subject(SubjectID)
    )
    ''')
    
    # Create Attendance table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Attendance (
        AttendanceID INTEGER PRIMARY KEY AUTOINCREMENT,
        StudentID INTEGER,
        Date DATE,
        Status TEXT,
        FOREIGN KEY(StudentID) REFERENCES Student(StudentID)
    )
    ''')
    
    # Insert sample data - Students
    cursor.execute("INSERT OR IGNORE INTO Student (StudentID, Name, Email, Course, Year) VALUES (1, 'Yuvraj Singh Sidhu', '24bcs10816@cuchd.in', 'BE', 2)")
    cursor.execute("INSERT OR IGNORE INTO Student (StudentID, Name, Email, Course, Year) VALUES (2, 'Aman Kumar', 'aman@email.com', 'BCA', 2)")
    cursor.execute("INSERT OR IGNORE INTO Student (StudentID, Name, Email, Course, Year) VALUES (3, 'Priya Sharma', 'priya@email.com', 'BE', 3)")
    cursor.execute("INSERT OR IGNORE INTO Student (StudentID, Name, Email, Course, Year) VALUES (4, 'Rahul Verma', 'rahul@email.com', 'BCA', 1)")
    
    # Insert sample data - Subjects
    cursor.execute("INSERT OR IGNORE INTO Subject (SubjectID, SubjectName, Course) VALUES (1, 'Database Management', 'BE')")
    cursor.execute("INSERT OR IGNORE INTO Subject (SubjectID, SubjectName, Course) VALUES (2, 'Operating Systems', 'BCA')")
    cursor.execute("INSERT OR IGNORE INTO Subject (SubjectID, SubjectName, Course) VALUES (3, 'Algorithms', 'BE')")
    cursor.execute("INSERT OR IGNORE INTO Subject (SubjectID, SubjectName, Course) VALUES (4, 'Networking', 'BCA')")
    
    # Insert sample data - Grades
    cursor.execute("INSERT OR IGNORE INTO Grade (GradeID, StudentID, SubjectID, Marks) VALUES (1, 1, 1, 90)")
    cursor.execute("INSERT OR IGNORE INTO Grade (GradeID, StudentID, SubjectID, Marks) VALUES (2, 2, 2, 85)")
    cursor.execute("INSERT OR IGNORE INTO Grade (GradeID, StudentID, SubjectID, Marks) VALUES (3, 3, 3, 78)")
    cursor.execute("INSERT OR IGNORE INTO Grade (GradeID, StudentID, SubjectID, Marks) VALUES (4, 4, 4, 82)")
    
    # Insert sample data - Attendance
    cursor.execute("INSERT OR IGNORE INTO Attendance (AttendanceID, StudentID, Date, Status) VALUES (1, 1, '2025-10-31', 'Present')")
    cursor.execute("INSERT OR IGNORE INTO Attendance (AttendanceID, StudentID, Date, Status) VALUES (2, 2, '2025-10-30', 'Absent')")
    cursor.execute("INSERT OR IGNORE INTO Attendance (AttendanceID, StudentID, Date, Status) VALUES (3, 3, '2025-10-29', 'Present')")
    cursor.execute("INSERT OR IGNORE INTO Attendance (AttendanceID, StudentID, Date, Status) VALUES (4, 4, '2025-10-28', 'Absent')")
    
    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == '__main__':
    create_database()
