from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import qrcode
import os

# Initialize Flask app
app = Flask(__name__)

# Ensure QR code storage directory exists
os.makedirs("static/qr_codes", exist_ok=True)

# Database file
DB_FILE = "students.db"

# Function to initialize the database
def init_db():
    """Create tables if they do not exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            index_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            grade TEXT NOT NULL,
            qr_code TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')
    conn.commit()
    conn.close()

# Function to generate QR code
def generate_qr(index_number):
    """Generate a QR code for a student and save it as an image."""
    qr = qrcode.make(index_number)
    qr_path = f"static/qr_codes/{index_number}.png"
    qr.save(qr_path)
    return qr_path

@app.route('/')
def index():
    """Render the main page with a list of students."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return render_template("index.html", students=students)

@app.route('/add', methods=['POST'])
def add_student():
    """Add a new student to the database."""
    index_number = request.form['index_number']
    name = request.form['name']
    grade = request.form['grade']

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO students (index_number, name, grade, qr_code) VALUES (?, ?, ?, ?)",
            (index_number, name, grade, "")
        )
        student_id = cursor.lastrowid
        qr_code_path = generate_qr(index_number)  # Generate QR code using index_number
        cursor.execute("UPDATE students SET qr_code = ? WHERE id = ?", (qr_code_path, student_id))
        conn.commit()
    except sqlite3.IntegrityError:
        return "Index number already exists!", 400
    finally:
        conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    # Initialize the database when the app starts
    init_db()
    app.run(debug=True)
