from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = '6457fghd@@'

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

# -- Route: Index

@app.route('/')
def index():
    
    return render_template('index.html')

if (__name__) == '__main__':
    init_db()
    app.run(debug=True)