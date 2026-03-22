from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('database.db')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
    ''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS students (
        roll_no TEXT PRIMARY KEY,
        name TEXT,
        enrollment_number TEXT,
        course TEXT,
        subject TEXT,
        submission TEXT,
        marks INTEGER,
        user TEXT
    )
    ''')

    conn.close()

init_db()

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect('database.db')
        try:
            conn.execute('INSERT INTO users VALUES (?, ?)', (user, pwd))
            conn.commit()
        except:
            return "Username already exists"
        finally:
            conn.close()

        return redirect('/login')

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect('database.db')
        result = conn.execute(
            'SELECT * FROM users WHERE username=? AND password=?',
            (user, pwd)
        ).fetchone()
        conn.close()

        if result:
            session['user'] = user
            return redirect('/')
        else:
            return "Invalid Login"

    return render_template('login.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# ---------------- HOME ----------------
@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')

    search = request.args.get('search')

    if search:
        students = conn.execute('''
        SELECT * FROM students 
        WHERE user=? AND (roll_no LIKE ? OR enrollment_number LIKE ?)
        ''', (session['user'], f'%{search}%', f'%{search}%')).fetchall()
    else:
        students = conn.execute(
            "SELECT * FROM students WHERE user=?",
            (session['user'],)
        ).fetchall()

    submitted = conn.execute(
        "SELECT COUNT(*) FROM students WHERE submission='Yes' AND user=?",
        (session['user'],)
    ).fetchone()[0]

    not_submitted = conn.execute(
        "SELECT COUNT(*) FROM students WHERE submission='No' AND user=?",
        (session['user'],)
    ).fetchone()[0]

    conn.close()

    return render_template(
        'index.html',
        students=students,
        submitted=submitted,
        not_submitted=not_submitted
    )

# ---------------- ADD ----------------
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        conn.execute('''
        INSERT INTO students 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form['roll_no'],
            request.form['name'],
            request.form['enrollment_number'],
            request.form['course'],
            request.form['subject'],
            request.form['submission'],
            request.form['marks'],
            session['user']
        ))
        conn.commit()
        conn.close()
        return redirect('/')

    return render_template('add.html')

# ---------------- DELETE ----------------
@app.route('/delete/<roll_no>')
def delete(roll_no):
    conn = sqlite3.connect('database.db')
    conn.execute(
        "DELETE FROM students WHERE roll_no=? AND user=?",
        (roll_no, session['user'])
    )
    conn.commit()
    conn.close()
    return redirect('/')

# ---------------- EDIT ----------------
@app.route('/edit/<roll_no>', methods=['GET', 'POST'])
def edit(roll_no):
    conn = sqlite3.connect('database.db')

    if request.method == 'POST':
        conn.execute('''
        UPDATE students SET
        name=?, enrollment_number=?, course=?,
        subject=?, submission=?, marks=?
        WHERE roll_no=? AND user=?
        ''', (
            request.form['name'],
            request.form['enrollment_number'],
            request.form['course'],
            request.form['subject'],
            request.form['submission'],
            request.form['marks'],
            roll_no,
            session['user']
        ))
        conn.commit()
        conn.close()
        return redirect('/')

    student = conn.execute(
        "SELECT * FROM students WHERE roll_no=? AND user=?",
        (roll_no, session['user'])
    ).fetchone()

    conn.close()
    return render_template('edit.html', student=student)


if __name__ == '__main__':
    app.run(debug=True)