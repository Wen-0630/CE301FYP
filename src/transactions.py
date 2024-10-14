from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, current_app, flash
from .models import Transaction, Loan, SavingGoal
import datetime
from bson.objectid import ObjectId

transactions = Blueprint('transactions', __name__)

@transactions.route('/transactions', methods=['GET'])
def list_transactions():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    transactions = Transaction.get_all_transactions_by_user(ObjectId(user_id))
    loans = Loan.get_all_loans_by_user(ObjectId(user_id))
    print(f"Retrieved transactions for user {user_id}: {transactions}")  # Debug statement
    return render_template('transactions.html', transactions=transactions, loans=loans)

@transactions.route('/transactions/add', methods=['GET', 'POST'])
def add_transaction():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        data = request.form.to_dict()
        
        if data.get('category') == 'Other':
            data['category'] = data.get('other_category')
        data.pop('other_category', None)

        if data.get('category') in ['Interest Expense', 'Loan Expense']:
            loan_name = data.pop('loan_name', None)
            user_id = session['user_id']
            loan = Loan.get_loan_by_name(loan_name, user_id)
            if data.get('category') == 'Interest Expense' and loan and float(data['amount']) > loan['interest_payable']:
                flash(f"Interest expense amount cannot exceed the loan's interest payable of {loan['interest_payable']:.2f}, please try again.")
                return redirect(url_for('transactions.list_transactions'))
            if data.get('category') == 'Loan Expense' and loan and float(data['amount']) > loan['outstanding_balance']:
                flash(f"Loan expense amount cannot exceed the loan's outstanding balance of {loan['outstanding_balance']:.2f}, please try again.")
                return redirect(url_for('transactions.list_transactions'))
            data['loan_name'] = loan_name

        data['userId'] = ObjectId(session['user_id'])
        data['amount'] = float(data['amount'])
        data['date'] = datetime.datetime.strptime(data['date'], '%Y-%m-%d')

        if 'payment_method' not in data:
            data['payment_method'] = None

        transaction = Transaction(
            userId=data['userId'],
            type=data['type'],
            category=data['category'],
            amount=data['amount'],
            date=data['date'],
            description=data['description'],
            payment_method=data.get('payment_method'),
            loan_name=data.get('loan_name')
        )
        transaction.save()

        if data.get('category') == 'Interest Expense' and loan:
            Loan.update_interest_expense(loan['name'], user_id)
        if data.get('category') == 'Loan Expense' and loan:
            Loan.update_loan_expense(loan['name'], user_id)

        # Recalculate current amount for each active saving goal
        saving_goals = SavingGoal.get_goals_by_user(session['user_id'])
        for goal in saving_goals:
            SavingGoal.calculate_current_amount(goal['_id'], session['user_id'])

        return redirect(url_for('transactions.list_transactions'))

    user_id = session['user_id']
    loans = Loan.get_all_loans_by_user(ObjectId(user_id))
    return render_template('transactions.html', loans=loans)

@transactions.route('/transactions/delete/<transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    Transaction.delete_transaction(ObjectId(transaction_id))  # Convert to ObjectId
    return redirect(url_for('transactions.list_transactions'))

@transactions.route('/transactions/edit/<transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    transaction = Transaction.get_transaction(ObjectId(transaction_id))

    if request.method == 'POST':
        data = request.form.to_dict()

        if data.get('category') == 'Other':
            data['category'] = data.get('other_category')
        data.pop('other_category', None)

        if data.get('category') in ['Interest Expense', 'Loan Expense']:
            loan_name = data.pop('loan_name', None)
            user_id = session['user_id']
            loan = Loan.get_loan_by_name(loan_name, user_id)
            if data.get('category') == 'Interest Expense' and loan and float(data['amount']) > loan['interest_payable']:
                flash(f"Interest expense amount cannot exceed the loan's interest payable of {loan['interest_payable']:.2f}, please try again.")
                return redirect(url_for('transactions.edit_transaction', transaction_id=transaction_id))
            if data.get('category') == 'Loan Expense' and loan and float(data['amount']) > loan['outstanding_balance']:
                flash(f"Loan expense amount cannot exceed the loan's outstanding balance of {loan['outstanding_balance']:.2f}, please try again.")
                return redirect(url_for('transactions.edit_transaction', transaction_id=transaction_id))
            data['loan_name'] = loan_name
            
        data['amount'] = float(data['amount'])
        data['date'] = datetime.datetime.strptime(data['date'], '%Y-%m-%d')

        Transaction.update_transaction(ObjectId(transaction_id), data)
        
        if data.get('category') == 'Interest Expense' and loan:
            Loan.update_interest_expense(loan['name'], user_id)
        if data.get('category') == 'Loan Expense' and loan:
            Loan.update_loan_expense(loan['name'], user_id)

        # Recalculate current amount for each active saving goal
        saving_goals = SavingGoal.get_goals_by_user(session['user_id'])
        for goal in saving_goals:
            SavingGoal.calculate_current_amount(goal['_id'], session['user_id'])

        return redirect(url_for('transactions.list_transactions'))

    user_id = session['user_id']
    loans = Loan.get_all_loans_by_user(ObjectId(user_id))
    return render_template('edit_transaction.html', transaction=transaction, loans=loans)

def calculate_total_income(user_id):
    total_income = current_app.mongo.db.transactions.aggregate([
        {"$match": {"userId": ObjectId(user_id), "type": "Income"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ])
    result = list(total_income)
    if result:
        return int(result[0]['total'])  # Convert the total to an integer
    return 0

def calculate_total_expense(user_id):
    total_expense = current_app.mongo.db.transactions.aggregate([
        {"$match": {"userId": ObjectId(user_id), "type": "Expense"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ])
    result = list(total_expense)
    if result:
        return int(result[0]['total'])  # Convert the total to an integer
    return 0

def calculate_total_transaction(user_id):
    total_income = calculate_total_income(user_id)
    total_expense = calculate_total_expense(user_id)
    return total_income - total_expense
