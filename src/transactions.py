from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, current_app, flash
from .models import Transaction, Loan, SavingGoal
from datetime import datetime, timedelta
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
        data['date'] = datetime.strptime(data['date'], '%Y-%m-%d')

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
        data['date'] = datetime.strptime(data['date'], '%Y-%m-%d')

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
    # Calculate total expense excluding credit card payments
    total_expense_excluding_credit_card = current_app.mongo.db.transactions.aggregate([
        {"$match": {"userId": ObjectId(user_id), "type": "Expense", "payment_method": {"$ne": "Credit Card"}}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ])
    
    result = list(total_expense_excluding_credit_card)
    total_expense = result[0]['total'] if result else 0

    return total_income - total_expense

@transactions.route('/api/income_categories_data', methods=['GET'])
def income_categories_data():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    try:
        user_id = ObjectId(session['user_id'])

        # Get the first and last day of the current month
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = SavingGoal.set_automatic_target_date()  # Last day of the month

        # Fetch income transactions within the current month
        income_transactions = list(current_app.mongo.db.transactions.find({
            "userId": user_id,
            "type": "Income",
            "date": {"$gte": start_of_month, "$lt": end_of_month + timedelta(days=1)}
        }))

        # Check if no transactions were found
        if not income_transactions:
            return jsonify({"categories": [], "values": []})

        # Group and sum transactions by category
        category_totals = {}
        for transaction in income_transactions:
            category = transaction['category']
            amount = transaction['amount']
            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount

        # Sort categories by total amount, descending
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

        # Select top 4 categories and group the rest under "Other"
        top_categories = sorted_categories[:4]
        other_total = sum(amount for _, amount in sorted_categories[4:])
        if other_total > 0:
            top_categories.append(("Other", other_total))

        # Prepare data for the Pie chart
        chart_data = {
            "categories": [category for category, _ in top_categories],
            "values": [amount for _, amount in top_categories]
        }

        return jsonify(chart_data)

    except Exception as e:
        print(f"Error in income_categories_data: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

@transactions.route('/api/expense_categories_data', methods=['GET'])
def expense_categories_data():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    try:
        user_id = ObjectId(session['user_id'])

        # Get the first and last day of the current month
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = SavingGoal.set_automatic_target_date()  # Last day of the month

        # Fetch expense transactions within the current month
        expense_transactions = list(current_app.mongo.db.transactions.find({
            "userId": user_id,
            "type": "Expense",
            "date": {"$gte": start_of_month, "$lt": end_of_month + timedelta(days=1)}
        }))

        # Check if no transactions were found
        if not expense_transactions:
            return jsonify({"categories": [], "values": []})

        # Group and sum transactions by category
        category_totals = {}
        for transaction in expense_transactions:
            category = transaction['category']
            amount = transaction['amount']
            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount

        # Sort categories by total amount, descending
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

        # Select top 4 categories and group the rest under "Other"
        top_categories = sorted_categories[:4]
        other_total = sum(amount for _, amount in sorted_categories[4:])
        if other_total > 0:
            top_categories.append(("Other", other_total))

        # Prepare data for the donut chart
        chart_data = {
            "categories": [category for category, _ in top_categories],
            "values": [amount for _, amount in top_categories]
        }

        return jsonify(chart_data)

    except Exception as e:
        print(f"Error in expense_categories_data: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

@transactions.route('/api/monthly_income_expense', methods=['GET'])
def monthly_income_expense():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401

    try:
        user_id = ObjectId(session['user_id'])
        current_year = datetime.now().year

        # Prepare an array to hold the results for each month
        monthly_data = {"income": [0] * 12, "expense": [0] * 12}

        # Fetch transactions for the current year
        transactions = list(current_app.mongo.db.transactions.find({
            "userId": user_id,
            "date": {"$gte": datetime(current_year, 1, 1), "$lt": datetime(current_year + 1, 1, 1)}
        }))

        # Aggregate totals by month
        for transaction in transactions:
            month_index = transaction['date'].month - 1  # Convert month to 0-based index
            if transaction['type'] == "Income":
                monthly_data["income"][month_index] += transaction['amount']
            elif transaction['type'] == "Expense":
                monthly_data["expense"][month_index] += transaction['amount']

        return jsonify(monthly_data)

    except Exception as e:
        print(f"Error in monthly_income_expense: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500
