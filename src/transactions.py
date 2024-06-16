from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, current_app
from .models import Transaction
import datetime
from bson.objectid import ObjectId

transactions = Blueprint('transactions', __name__)

@transactions.route('/transactions', methods=['GET'])
def list_transactions():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    transactions = Transaction.get_all_transactions_by_user(ObjectId(user_id))  # Convert to ObjectId
    print(f"Retrieved transactions for user {user_id}: {transactions}")  # Debug statement
    return render_template('transactions.html', transactions=transactions)

@transactions.route('/transactions/add', methods=['POST'])
def add_transaction():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    data = request.form.to_dict()
    
    if data.get('category') == 'Other':
        data['category'] = data.get('other_category')
    
    # Remove 'other_category' from data as it is not needed anymore
    data.pop('other_category', None)
    
    data['userId'] = ObjectId(session['user_id'])  # Convert to ObjectId
    data['amount'] = float(data['amount'])
    data['date'] = datetime.datetime.strptime(data['date'], '%Y-%m-%d')
    
    transaction = Transaction(**data)
    transaction.save()
    
    return redirect(url_for('transactions.list_transactions'))

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
        # Remove 'other_category' from data as it is not needed anymore
        data.pop('other_category', None)

        data['amount'] = float(data['amount'])
        data['date'] = datetime.datetime.strptime(data['date'], '%Y-%m-%d')

        # Remove other_category key from the original transaction data if it exists and the new category is not 'Other'
        if 'other_category' in transaction and data['category'] != 'Other':
            transaction.pop('other_category', None)

        Transaction.update_transaction(ObjectId(transaction_id), data)
        
        return redirect(url_for('transactions.list_transactions'))
    
    return render_template('edit_transaction.html', transaction=transaction)