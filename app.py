from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# MySQL Connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',  # Replace with your MySQL username
        password='',  # Replace with your MySQL password (leave empty if no password)
        database='StudentRegistration'
    )

@app.route('/register', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        course_id = request.form['course']

        # Insert student into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Students (name, email, age, course_id)
            VALUES (%s, %s, %s, %s)
        ''', (name, email, age, course_id))
        conn.commit()

        # Get the newly inserted student_id
        cursor.execute('SELECT LAST_INSERT_ID()')
        student_id = cursor.fetchone()[0]

        # Insert into Registrations table
        cursor.execute('''
            INSERT INTO Registrations (student_id, course_id)
            VALUES (%s, %s)
        ''', (student_id, course_id))
        conn.commit()

        conn.close()

        # Flash success message
        flash("You have been successfully registered!", "success")

        # Redirect to home page after successful registration
        return redirect('/')

    # If GET request, render registration page
    return render_template('index.html')

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch courses for the dropdown
    cursor.execute('SELECT course_id, course_name FROM Courses')
    courses = cursor.fetchall()

    # Fetch courses and their assignments
    cursor.execute('''SELECT c.course_name, a.assignment_name, a.due_date
                      FROM Courses c
                      JOIN Assignments a ON c.course_id = a.course_id''')
    assignments = cursor.fetchall()

    conn.close()

    # Pass both courses and assignments to the homepage template
    return render_template('index.html', courses=courses, assignments=assignments)

@app.route('/add_instructor', methods=['GET', 'POST'])
def add_instructor():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']

        cursor.execute('INSERT INTO Instructors (name, email, department) VALUES (%s, %s, %s)',
                       (name, email, department))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))

    conn.close()
    return render_template('add_instructor.html')

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Students (name, email, age) VALUES (%s, %s, %s)', (name, email, age))
        conn.commit()
        conn.close()
        
        return redirect(url_for('home'))  # Redirect to home after adding student
    
    return render_template('add_student.html')  # Render the add_student.html form

@app.route('/view_assignments')
def view_assignments():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all assignments with their course names
    cursor.execute('''SELECT c.course_name, a.assignment_name, a.due_date
                      FROM Courses c
                      JOIN Assignments a ON c.course_id = a.course_id''')
    assignments = cursor.fetchall()
    conn.close()

    return render_template('assignments.html', assignments=assignments)  # Render assignments page

@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch available instructors from the Instructors table
    cursor.execute('SELECT instructor_id, name, department FROM Instructors')
    instructors = cursor.fetchall()

    if request.method == 'POST':
        course_name = request.form['course_name']
        course_description = request.form['course_description']
        instructor_id = request.form['instructor_id']
        
        # Insert the course into the Courses table with a valid instructor_id
        cursor.execute('INSERT INTO Courses (course_name, course_description, instructor_id) VALUES (%s, %s, %s)',
                       (course_name, course_description, instructor_id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('home'))  # Redirect to home after adding the course

    conn.close()
    return render_template('add_course.html', instructors=instructors)  # Pass instructors to template

@app.route('/assignments')
def assignments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT assignment_name, due_date FROM Assignments;')
    assignments = cursor.fetchall()
    conn.close()
    return render_template('assignments.html', assignments=assignments)

@app.route('/add_assignment', methods=['GET', 'POST'])
def add_assignment():
    if request.method == 'POST':
        assignment_name = request.form['assignment_name']
        due_date = request.form['due_date']
        course_id = request.form['course_id']  # Get the course_id from the form

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert the new assignment
        cursor.execute('''INSERT INTO Assignments (course_id, assignment_name, due_date)
                          VALUES (%s, %s, %s)''', (course_id, assignment_name, due_date))

        conn.commit()
        conn.close()

        # Redirect back to home or view assignments page
        return redirect('/view_assignments')

    # If the request is GET, display the form
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT course_id, course_name FROM Courses')
    courses = cursor.fetchall()
    conn.close()

    return render_template('add_assignment.html', courses=courses)  # Pass courses to the template

if __name__ == '__main__':
    app.run(debug=True)
    print("Flask app is running...")