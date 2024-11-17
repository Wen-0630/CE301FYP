# src/loan.py
from flask import Blueprint, request, render_template, redirect, url_for, session
from .models import Loan
import datetime
from bson.objectid import ObjectId

loan = Blueprint('loan', __name__)

@loan.route('/loans', methods=['GET'])
def list_loans():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    loans = Loan.get_all_loans_by_user(ObjectId(user_id))
    interest_expenses = Loan.get_total_interest_expense_by_loan(ObjectId(user_id))
    loan_expenses = Loan.get_total_loan_expense_by_loan(ObjectId(user_id))
    
    # Update interest_expense in loans based on calculated values
    for loan in loans:
        loan['interest_expense'] = interest_expenses.get(loan['name'], 0)
        loan['loan_expense'] = loan_expenses.get(loan['name'], 0)
        loan['interest_balance'] = loan['interest_payable'] - loan['interest_expense']
        loan['outstanding_balance'] = loan['original_amount'] - loan['loan_expense']

        update_data = {
            'interest_balance': loan['interest_balance'],
            'outstanding_balance': loan['outstanding_balance']
        }
        Loan.update_loan(loan['_id'], update_data)
    
    return render_template('loan.html', loans=loans)

@loan.route('/loans/add', methods=['POST'])
def add_loan():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    name = request.form['name']
    loan_type = request.form['loan_type']
    original_amount = float(request.form['original_amount'])
    loan_term = int(request.form['loan_term'])
    repayment_term = request.form['repayment_term']
    interest_rate = float(request.form['interest_rate'])
    interest_payable = float(request.form['interest_payable'])
    issue_date = datetime.datetime.strptime(request.form['issue_date'], '%Y-%m-%d')
    maturity_date = datetime.datetime.strptime(request.form['maturity_date'], '%Y-%m-%d')
    description = request.form.get('description', None)

    # Calculate the missing fields
    outstanding_balance = original_amount  # Initial outstanding balance is the loan amount
    interest_expense = 0  # Initially, there are no interest expenses
    loan_expense = 0  # Initially, there are no loan expenses

    loan = Loan(
        userId=user_id, 
        name=name,
        loan_type=loan_type, 
        original_amount=original_amount, 
        loan_term=loan_term, 
        repayment_term=repayment_term, 
        interest_rate=interest_rate, 
        outstanding_balance=outstanding_balance, 
        interest_payable=interest_payable, 
        interest_expense=interest_expense, 
        loan_expense=loan_expense, 
        issue_date=issue_date, 
        maturity_date=maturity_date, 
        description=description
    )
    loan.save()
    
    return redirect(url_for('loan.list_loans'))


@loan.route('/loans/edit/<loan_id>', methods=['GET', 'POST'])
def edit_loan(loan_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form['name']
        loan_type = request.form['loan_type']
        original_amount = float(request.form['original_amount'])
        loan_term = int(request.form['loan_term'])
        repayment_term = request.form['repayment_term']
        interest_rate = float(request.form['interest_rate'])
        interest_payable = float(request.form['interest_payable'])
        issue_date = datetime.datetime.strptime(request.form['issue_date'], '%Y-%m-%d')
        maturity_date = datetime.datetime.strptime(request.form['maturity_date'], '%Y-%m-%d')
        description = request.form.get('description', None)

        update_data = {
            'name': name,
            'loan_type': loan_type,
            'original_amount': original_amount,
            'loan_term': loan_term,
            'repayment_term': repayment_term,
            'interest_rate': interest_rate,
            'interest_payable': interest_payable,
            'issue_date': issue_date,
            'maturity_date': maturity_date,
            'description': description
        }

        Loan.update_loan(ObjectId(loan_id), update_data)
        return redirect(url_for('loan.list_loans'))

    loan = Loan.get_loan(ObjectId(loan_id))
    return render_template('edit_loan.html', loan=loan)

@loan.route('/loans/delete/<loan_id>', methods=['POST'])
def delete_loan(loan_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    Loan.delete_loan(ObjectId(loan_id))
    return redirect(url_for('loan.list_loans'))
