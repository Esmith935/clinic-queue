# impor chatbot
import google.generativeai as genai 
#other imports
from flask import Flask, render_template, redirect, url_for, request, flash, session,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = '6457fghd@@'

staff_key = "Password1"

DATABASE = 'database.db'

# -- Get Website Display Name :

def get_displayname():
    displayname = open("displayname.txt", "r").read()
    return displayname

# -- Initialise Database

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
                customeremail TEXT NOT NULL,
                date TEXT NOT NULL
            )
        ''')

        conn.commit()

## -------------------- ##
# -- Auth routes -- #
## -------------------- ##

# -- Route: Register (Staff)
@app.route('/register_staff', methods=['GET', 'POST'])
def register_staff():
    registered = False
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

    return render_template('register_staff.html', registered = registered, displayname = get_displayname())

# -- Route: Login (Staff)

@app.route('/login-staff', methods=['GET', 'POST'])
def login_staff():
    registered = False
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

    return render_template('login-staff.html', registered = registered, displayname = get_displayname())

# -- Route: Register (User)

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    registered = False
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

    return render_template('register_user.html', registered = registered, displayname = get_displayname())


# -- Route: Login (User)

@app.route('/login-user', methods=['GET', 'POST'])
def login_user():
    registered = False
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

    return render_template('login-user.html', registered = registered, displayname = get_displayname())

# -- Route: Logout

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('index'))

## -------------------- ##
## -------------------- ##
## -------------------- ##

# -- Route: Index

@app.route('/')
def index():
    registered = False
    if 'email' in session:

        registered = True
    
    return render_template('index.html', registered = registered, displayname = get_displayname())

# -- Route: Staff Dashboard

@app.route('/staff-dash')
def staff_dash():
    registered = False
    if 'email' not in session:

        return redirect(url_for('login_staff'))
    else: registered = True

    return render_template('staff-dash.html', registered = registered, displayname = get_displayname())

# -- Route: Queue Dashboard

@app.route('/wait-dash')
def queue_dash():
    registered = False
    if 'email' not in session:

        return redirect(url_for('login_user'))
    else: registered = True
    
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


    return render_template('wait-dash.html', queue_number = queue_number, registered = registered, displayname = get_displayname())

# -- Route: User Dashboard

@app.route('/user-dash')
def user_dash():
    registered = False
    if 'email' not in session:

        return redirect(url_for('login_user'))
    else: registered = True

    return render_template('user-dash.html', registered = registered, displayname = get_displayname())

# -- Route: Book Appointment

@app.route('/book', methods=['GET', 'POST'])
def book_appointment():
    registered = False
    if 'email' not in session:

        return redirect(url_for('login_user'))
    else: registered = True
    
    if request.method == 'POST':
        date = request.form.get('date')
        time = request.form.get('time')
        customeremail = session['email']

        #combine date and time into a single datetime string
        appointemt_datetime = f"{date} {time}"

        with sqlite3.connect(DATABASE) as conn:
            user = conn.execute('SELECT id FROM users WHERE email = ?', (customeremail,)).fetchone()
            if user:
                conn.execute('INSERT INTO bookings (customeremail, date) VALUES (?, ?)', 
                            (customeremail, appointemt_datetime))
                conn.commit()
                flash('Appointment booked successfully.')

            return redirect(url_for('user_dash'))

    return render_template('book.html', registered = registered, displayname = get_displayname())

# -- Route: Manage Bookings

@app.route('/manage-bookings')
def manage_bookings():
    registered = False
    if 'email' not in session:

        return redirect(url_for('login_staff'))
    else: registered = True
    
    with sqlite3.connect(DATABASE) as conn:
        bookings = conn.execute('SELECT * FROM bookings').fetchall()
    
    return render_template('manage-bookings.html', bookings = bookings, registered = registered, displayname = get_displayname())

# -- Route: Manage Queue

@app.route('/manage-queue')
def manage_queue():
    registered = False
    if 'email' not in session:

        return redirect(url_for('login_staff'))
    else: registered = True
    
    with sqlite3.connect(DATABASE) as conn:
        # Join with users table to get the names of people in the queue
        #tickets = conn.execute('''
        #    SELECT tickets.id, users.name, tickets.customeremail 
        #    FROM tickets 
        #    JOIN users ON tickets.customeremail = users.email
        #    ORDER BY tickets.id ASC
        #''').fetchall()

        tickets = conn.execute('''
            SELECT * FROM tickets
        ''').fetchall()

    #print(tickets)
    return render_template('manage-queue.html', tickets = tickets, registered = registered, displayname = get_displayname())

# -- Route: Customise Website Aesthetic
@app.route('/customise', methods=['GET', 'POST'])
def customise():
    registered = False
    if 'email' not in session:
        return redirect(url_for('login_staff'))
    
    if request.method == 'POST':
        displayname = request.form['displayname']

        with open("clinic-queue/displayname.txt", "w") as f:
            f.write(displayname)

        flash("Rewrite successful")
        return(redirect(url_for('staff_dash')))


    return render_template('customise.html', registered = registered, displayname = get_displayname())

# -- Route: Delete Ticket
@app.route('/delete_ticket/<int:ticket_id>', methods=['GET', 'POST'])
def delete_ticket(ticket_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('DELETE FROM tickets WHERE id = ?', (ticket_id,))
        conn.commit()
    return redirect(url_for('manage_queue'))

# -- Route: Delete Bookings
@app.route('/delete_booking/<int:booking_id>', methods=['GET', 'POST'])
def delete_booking(booking_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
        conn.commit()
    return redirect(url_for('manage_bookings'))

if (__name__) == '__main__':
    init_db()
    app.run(debug=True)