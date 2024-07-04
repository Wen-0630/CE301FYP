# src/creditCard.py
from flask import Blueprint, request, render_template, redirect, url_for, session, current_app
from .models import Transaction, Repayment
import datetime
from bson.objectid import ObjectId

credit_card = Blueprint('credit_card', __name__)

@credit_card.route('/credit_cards', methods=['GET'])
def list_credit_cards():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    credit_card_transactions = Transaction.get_credit_card_transactions_by_user(ObjectId(user_id))
    for transaction in credit_card_transactions:
        transaction['repayments'] = Repayment.get_repayments_by_transaction(transaction['_id'])
    return render_template('creditCard.html', credit_card_transactions=credit_card_transactions)

@credit_card.route('/credit_cards/update_repayment', methods=['POST'])
def update_repayment():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    transaction_id = request.form['transaction_id']
    repayment_amount = float(request.form['repayment_amount'])
    repayment_date = datetime.datetime.strptime(request.form['repayment_date'], '%Y-%m-%d')

    transaction = Transaction.get_transaction(ObjectId(transaction_id))
    remaining_amount = transaction.get('remaining_amount', transaction['amount']) - repayment_amount

    Repayment.add_repayment(transaction_id, repayment_amount, repayment_date)

    update_data = {
        'repayment_date': repayment_date,
        'remaining_amount': remaining_amount
    }
    
    if remaining_amount <= 0:
        update_data['repayment_status'] = 'Paid'
        update_data['remaining_amount'] = 0
    else:
        update_data['repayment_status'] = 'Pending'
    
    Transaction.update_transaction(ObjectId(transaction_id), update_data)
    
    return redirect(url_for('credit_card.list_credit_cards'))

@credit_card.route('/credit_cards/delete_repayment', methods=['POST'])
def delete_repayment():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    repayment_id = request.form['repayment_id']
    repayment = Repayment.get_repayment(ObjectId(repayment_id))
    
    if repayment:
        transaction_id = repayment['transaction_id']
        repayment_amount = repayment['repayment_amount']

        transaction = Transaction.get_transaction(ObjectId(transaction_id))
        new_remaining_amount = transaction.get('remaining_amount', transaction['amount']) + repayment_amount

        update_data = {
            'remaining_amount': new_remaining_amount,
            'repayment_status': 'Pending' if new_remaining_amount > 0 else 'Paid'
        }

        Transaction.update_transaction(ObjectId(transaction_id), update_data)
        Repayment.delete_repayment(ObjectId(repayment_id))

    return redirect(url_for('credit_card.list_credit_cards'))

def get_total_outstanding(user_id):
    credit_card_transactions = Transaction.get_credit_card_transactions_by_user(ObjectId(user_id))
    total_outstanding = sum(t.get('remaining_amount', t['amount']) for t in credit_card_transactions)
    return total_outstanding

def get_total_repayment_amount(user_id):
    # Aggregate the total repayment amount for each expense transaction
    total_repayment_amount = current_app.mongo.db.repayments.aggregate([
        {"$lookup": {
            "from": "transactions",
            "localField": "transaction_id",
            "foreignField": "_id",
            "as": "transaction"
        }},
        {"$unwind": "$transaction"},
        {"$match": {"transaction.userId": ObjectId(user_id), "transaction.payment_method": "Credit Card"}},
        {"$group": {"_id": None, "total_repayment": {"$sum": "$repayment_amount"}}}
    ])
    
    result = list(total_repayment_amount)
    if result:
        return result[0]['total_repayment']  # Return the total repayment amount
    return 0
