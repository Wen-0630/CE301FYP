#src/views.py
from flask import Blueprint, redirect, url_for, render_template, session
from .models import Transaction
from bson.objectid import ObjectId
from .transactions import calculate_total_income, calculate_total_expense

# Create a Blueprint for user-related routes
views = Blueprint('user', __name__, template_folder='templates')

@views.route('/')
def home():
    return redirect(url_for('auth.login'))

@views.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    total_income = calculate_total_income(user_id)
    total_expense = calculate_total_expense(user_id)
    
    return render_template('dashboard.html', total_income=total_income, total_expense=total_expense)

@views.route('/transactions')
def transactions():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    transactions = Transaction.get_all_transactions_by_user(ObjectId(user_id))
    print(f"Retrieved transactions for user {user_id}: {transactions}")  # Debug statement
    return render_template('transactions.html', transactions=transactions)
