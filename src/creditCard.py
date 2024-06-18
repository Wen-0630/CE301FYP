# src/creditCard.py
from flask import Blueprint, request, render_template, redirect, url_for, session, current_app
from .models import Transaction
import datetime
from bson.objectid import ObjectId

credit_card = Blueprint('credit_card', __name__)

@credit_card.route('/credit_cards', methods=['GET'])
def list_credit_cards():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    credit_card_transactions = Transaction.get_credit_card_transactions_by_user(ObjectId(user_id))
    return render_template('creditCard.html', credit_card_transactions=credit_card_transactions)

@credit_card.route('/credit_cards/update_repayment', methods=['POST'])
def update_repayment():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    transaction_id = request.form['transaction_id']
    repayment_amount = float(request.form['repayment_amount'])
    due_date = datetime.datetime.strptime(request.form['due_date'], '%Y-%m-%d')

    transaction = Transaction.get_transaction(ObjectId(transaction_id))
    remaining_amount = transaction.get('remaining_amount', transaction['amount']) - repayment_amount

    update_data = {
        'due_date': due_date,
        'remaining_amount': remaining_amount
    }
    
    if remaining_amount <= 0:
        update_data['repayment_status'] = 'Paid'
        update_data['remaining_amount'] = 0
    else:
        update_data['repayment_status'] = 'Pending'
    
    Transaction.update_transaction(ObjectId(transaction_id), update_data)
    
    return redirect(url_for('credit_card.list_credit_cards'))

def get_total_outstanding(user_id):
    credit_card_transactions = Transaction.get_credit_card_transactions_by_user(ObjectId(user_id))
    total_outstanding = sum(t.get('remaining_amount', t['amount']) for t in credit_card_transactions)
    return total_outstanding