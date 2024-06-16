from flask import session, Blueprint, request, render_template, flash, redirect, url_for, current_app
from werkzeug.security import check_password_hash, generate_password_hash
import re
from bson.objectid import ObjectId

auth = Blueprint('auth', __name__, template_folder='../templates')

def create_user(mongo, user_data):
    mongo.cx['CE-301'].users.insert_one(user_data)  # Insert into "users" collection

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower()  # Convert email to lowercase
        password = request.form['password']
        print(f"Login attempt with email: {email}")  # Debug statement
        if authenticate_user(current_app.mongo, email, password):
            print("Authentication successful")  # Debug statement
            flash('Login successful!', category='success')
            return redirect(url_for('user.dashboard'))
        else:
            print("Authentication failed")  # Debug statement
            flash('Alert: Incorrect username or password. Please try again.', category='error')
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()  # Clear the session to log out the user
    flash('You have been logged out.', category='info')
    return redirect(url_for('auth.login'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email'].lower()  # Convert email to lowercase
        password = request.form['password']
        print(f"Signup attempt with email: {email}, username: {username}")  # Debug statement
        if not username or not email or not password:
            flash('Please fill out all fields', category='error')
        else:
            if len(password) < 8 or not re.search("[a-z]", password) or not re.search("[A-Z]", password) or not re.search("[0-9]", password) or not re.search("[!@#$%^&*]", password):
                flash('Alert: Password must be at least 8 characters long and include a mix of letters, numbers, and symbols', category='error')
            else:
                mongo = current_app.mongo
                user_exists = mongo.cx['CE-301'].users.find_one({'email': email})
                if user_exists:
                    flash('Alert: Email address already in use', category='error')
                else:
                    bcrypt = current_app.bcrypt
                    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                    user_data = {'username': username, 'email': email, 'password': hashed_password}
                    create_user(mongo, user_data)
                    print("User registered successfully")  # Debug statement
                    flash('Registration successful! Please log in.', category='success')
                    return redirect(url_for('auth.login'))
        
    return render_template('signup.html')

def authenticate_user(mongo, email, password):
    print(f"Attempting to authenticate user with email: {email}")  # Debug statement
    user = mongo.cx['CE-301'].users.find_one({"email": email})  # Retrieve from "users" collection
    print(f"Query executed. Result: {user}")  # Debug statement
    if user:
        print(f"User found: {user}")  # Debug statement
        bcrypt = current_app.bcrypt
        if bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])  # Store user ID as a string
            print(f"User authenticated: {user['_id']}")  # Debug statement
            return True
        else:
            print("Password check failed")  # Debug statement
    else:
        print("User not found")  # Debug statement
    return False
