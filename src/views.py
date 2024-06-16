#src/views.py
from flask import Blueprint, redirect, url_for, render_template, session

# Create a Blueprint for user-related routes
views = Blueprint('user', __name__, template_folder='templates')

@views.route('/')
def home():
    return redirect(url_for('auth.login'))

@views.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        print("User not authenticated")  # Debug statement
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')

@views.route('/transactions')
def transactions():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('transactions.html')
