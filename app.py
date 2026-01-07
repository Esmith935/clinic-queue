from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = '6457fghd@@'

staff_key = "Password1"

DATABASE = 'database.db'

# -- Initialise database

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''') # Tickets for queue


        conn.execute('''
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customerid INTEGER NOT NULL UNIQUE
            )
        ''')

        conn.execute('''
                CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customerid INTEGER NOT NULL UNIQUE,
                date DATETIME NOT NULL
            )
        ''')


        conn.commit()

## -------------------- ##
# -- Auth routes -- #
## -------------------- ##

# -- Route: Register (Staff)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form['email'].lower()
        password = generate_password_hash(request.form['password'])
        staff_key_input = request.form['staff_key']

        if staff_key_input != staff_key:
            print('Invalid staff key!')
            flash('Invalid staff key!')
            return redirect(url_for('index'))
            

        try:
            with sqlite3.connect(DATABASE) as conn:
                conn.execute('INSERT INTO staff (email, password) VALUES  (?, ?)', (email, password))
                conn.commit()
            print("Registration successful")
            flash("Registration successful")
            return redirect(url_for('staff-dash'))

        except sqlite3.IntegrityError:
            print("Username already in use.")
            flash("Username already in use.")
            return redirect(url_for('register'))

    return render_template('register.html')

## -------------------- ##

# -- Route: Index

@app.route('/')
def index():
    
    return render_template('index.html')

# -- Route: Staff Dashboard

@app.route('/staff-dash')
def staff_dash():

    return render_template('staff-dash.html')

# -- Route: Queue Dashboard

@app.route('/queue-dash')
def queue_dash():

    return render_template('queue-dash.html')

# -- Route: User Dashboard

@app.route('/user-dash')
def user_dash():

    return render_template('user-dash.html')

if (__name__) == '__main__':
    init_db()
    app.run(debug=True)