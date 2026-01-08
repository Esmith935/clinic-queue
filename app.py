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
                name TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''') # Tickets for queue


        conn.execute('''
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customeremail TEXT NOT NULL UNIQUE
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
@app.route('/register_staff', methods=['GET', 'POST'])
def register_staff():
    if 'email' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form['email'].lower()
        name = request.form['name']
        password = generate_password_hash(request.form['password'])
        staff_key_input = request.form['staff_key']

        if staff_key_input != staff_key:
            print('Invalid staff key!')
            flash('Invalid staff key!')
            return redirect(url_for('index'))
            

        try:
            with sqlite3.connect(DATABASE) as conn:
                conn.execute('INSERT INTO staff (email, name, password) VALUES (?, ?, ?)', (email, name, password))
                conn.commit()
            print("Registration successful")
            flash("Registration successful")
            return redirect(url_for('staff_dash'))

        except sqlite3.IntegrityError:
            print("Username already in use.")
            flash("Username already in use.")
            return redirect(url_for('register_staff'))

    return render_template('register_staff.html')

# -- Route: Login (Staff)

@app.route('/login-staff', methods=['GET', 'POST'])
def login_staff():
    if 'email' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = (request.form['email']).lower()
        password_input = request.form['password']
        staff_key_input = request.form['staff_key']

        if staff_key_input != staff_key:
            print('Invalid staff key!')
            flash('Invalid staff key!')
            return redirect(url_for('index'))
        
        with sqlite3.connect(DATABASE) as conn:
            user = conn.execute('SELECT * FROM staff WHERE email = ?', (email,)).fetchone()
        if user and check_password_hash(user[3], password_input):
            session['email'] = email
            flash('Login successful.')
            return redirect(url_for('staff_dash'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('login_staff'))

    return render_template('login-staff.html')

# -- Route: Register (User)

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if 'email' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form['email'].lower()
        name = request.form['name']
        password = generate_password_hash(request.form['password'])

        try:
            with sqlite3.connect(DATABASE) as conn:
                conn.execute('INSERT INTO users (email, name, password) VALUES (?, ?, ?)', (email, name, password))
                conn.commit()
            print("Registration successful")
            flash("Registration successful")
            return redirect(url_for('user_dash'))

        except sqlite3.IntegrityError:
            print("Username already in use.")
            flash("Username already in use.")
            return redirect(url_for('register_user'))

    return render_template('register_user.html')


# -- Route: Login (User)

@app.route('/login-user', methods=['GET', 'POST'])
def login_user():
    if 'email' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = (request.form['email']).lower()
        password_input = request.form['password']

        with sqlite3.connect(DATABASE) as conn:
            user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if user and check_password_hash(user[3], password_input):
            session['email'] = email
            flash('Login successful.')
            return redirect(url_for('user_dash'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('login_user'))

    return render_template('login-user.html')

# -- Route: Logout

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('index'))

## -------------------- ##

# -- Route: Index

@app.route('/')
def index():
    
    return render_template('index.html')

# -- Route: Staff Dashboard

@app.route('/staff-dash')
def staff_dash():
    if 'email' not in session:

        return redirect(url_for('login_staff'))

    return render_template('staff-dash.html')

# -- Route: Queue Dashboard

@app.route('/wait-dash')
def queue_dash():
    if 'email' not in session:

        return redirect(url_for('login_user'))
    
    email = session['email']
    
    with sqlite3.connect(DATABASE) as conn:
        ticketExists = conn.execute('SELECT * FROM tickets WHERE customeremail = ?', (email,)).fetchone()
        if ticketExists:
            tickets = conn.execute('SELECT * FROM tickets').fetchall()
            n = 0

            for i in tickets:
                n += 1

                if i[1] == email:
                    queue_number = n

                    break
            
        else:
            conn.execute('INSERT INTO tickets (customeremail) VALUES (?)', (email,))

            return redirect(url_for('queue_dash'))


    return render_template('wait-dash.html', queue_number = queue_number)

# -- Route: User Dashboard

@app.route('/user-dash')
def user_dash():
    if 'email' not in session:

        return redirect(url_for('login_user'))

    return render_template('user-dash.html')


# -- Route: Book Appointment
@app.route('/book')
def book_appointment():
    if 'email' not in session:
        return redirect(url_for('login_user'))

    return render_template('book.html')

if (__name__) == '__main__':
    init_db()
    app.run(debug=True)