#src/views.py
from flask import Blueprint, redirect, url_for, render_template, session, current_app, jsonify, request, flash
from werkzeug.utils import secure_filename
from .models import Transaction, Loan, SavingGoal
from bson.objectid import ObjectId
from .transactions import calculate_total_income, calculate_total_expense
from .creditCard import get_total_outstanding
from .investment import calculate_total_investment_profit_loss
from .cashFlow import get_net_cash_flow
from .budget import BudgetManager 
from .notifications import Notification, send_income_expense_ratio_notification, send_budget_vs_spending_notification
from .other_assets import OtherAsset
from .other_liabilities import OtherLiability
from .todo import get_tasks
from .utils import get_crypto_data
import datetime 
import json
import os

# Create a Blueprint for user-related routes
views = Blueprint('user', __name__, template_folder='templates')

def get_dashboard_data(user_id):
    user = current_app.mongo.cx['CE-301'].users.find_one({"_id": ObjectId(user_id)})
    if 'profile_pic' not in user:
        user['profile_pic'] = 'default_profile.jpeg'

    total_income = calculate_total_income(user_id)
    total_expense = calculate_total_expense(user_id)
    total_credit_card_outstanding = get_total_outstanding(user_id)
    loans = Loan.get_all_loans_by_user(ObjectId(user_id))
    total_loan_outstanding = sum(loan['outstanding_balance'] + loan['interest_balance'] for loan in loans)
    total_other_liabilities = OtherLiability.get_total_other_liabilities(user_id)
    total_outstanding = total_credit_card_outstanding + total_loan_outstanding + total_other_liabilities

    total_investment = calculate_total_investment_profit_loss(user_id)
    net_cash_flow = get_net_cash_flow(user_id)
    total_other_assets = OtherAsset.get_total_other_assets(user_id)
    total_assets = net_cash_flow + total_other_assets
    net_worth = total_assets + total_investment - total_outstanding

    saving_goals = SavingGoal.get_goals_by_user(user_id)
    for goal in saving_goals:
        SavingGoal.calculate_current_amount(goal['_id'], user_id)

    if total_expense > 0:
        income_expense_ratio = round((total_expense / total_income) * 100, 2)
    elif total_income > 0:
        income_expense_ratio = 0.00  # Set the ratio to 0 if income exists but expense is nil
    else:
        income_expense_ratio = 100.00

    budget = BudgetManager.get_latest_budget(user_id)
    radar_data = BudgetManager.prepare_radar_chart_data(
        user_id,
        budget['categories'] if budget else [],
        budget['budget_amounts'] if budget else [],
        budget['start_date'] if budget else None,
        budget['end_date'] if budget else None
    ) if budget else {}
    radar_data_json = json.dumps(radar_data)
    budget_message = "No active budget. Please set a budget." if not budget else ""

    notifications = Notification.get_active_notifications(user_id)
    top_asset_categories, total_amount = get_top_asset_categories(user_id)
    sorted_loans = sorted(loans, key=lambda x: x['original_amount'], reverse=True)
    top_5_loans = sorted_loans[:5]

    tasks = list(current_app.mongo.db.todo_tasks.find({"user_id": ObjectId(user_id)}))
    for task in tasks:
        task['_id'] = str(task['_id'])

    # Query the crypto holdings, sort by profit/loss in descending order, and limit to top 5
    top_crypto_performance = list(
        current_app.mongo.db.crypto_holdings.find({'userId': ObjectId(user_id)})
        .sort('profit_loss', -1)
        .limit(5)
    )

    # Extract asset names of top-performing crypto
    top_crypto_names = [holding['asset'] for holding in top_crypto_performance]

    # Fetch current market data for all crypto assets
    market_data = get_crypto_data()
    
    # Map each crypto name to its current market price using lowercase comparison for matching
    current_prices = {crypto['name'].lower(): crypto['current_price'] for crypto in market_data}

    # Construct a list of dictionaries with asset names and their current prices
    top_crypto_with_prices = [
        {"name": asset_name, "current_price": current_prices.get(asset_name.lower(), "N/A")}
        for asset_name in top_crypto_names
    ]

    return {
        "user": user,
        "total_income": total_income,
        "total_expense": total_expense,
        "total_credit_card_outstanding": total_credit_card_outstanding,
        "loans": loans,
        "total_loan_outstanding": total_loan_outstanding,
        "total_other_liabilities": total_other_liabilities,
        "total_outstanding": total_outstanding,
        "total_investment": total_investment,
        "net_cash_flow": net_cash_flow,
        "total_assets": total_assets,
        "net_worth": net_worth,
        "saving_goals": saving_goals,
        "income_expense_ratio": income_expense_ratio,
        "budget_message": budget_message,
        "radar_data_json": radar_data_json,
        "notifications": notifications,
        "top_asset_categories": top_asset_categories,
        "top_5_loans": top_5_loans, 
        "total_amount": total_amount,
        "tasks": tasks,
        "top_crypto_names": top_crypto_names,
        "top_crypto_with_prices": top_crypto_with_prices
    }
    
@views.route('/')
def home():
    return redirect(url_for('auth.login'))

@views.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    data = get_dashboard_data(user_id)

    return render_template('dashboard.html', 
                           user=data['user'],
                           total_income=data['total_income'], 
                           total_expense=data['total_expense'], 
                           total_outstanding=data['total_outstanding'], 
                           total_investment=data['total_investment'], 
                           total_assets=data['total_assets'],
                           net_worth=data['net_worth'],
                           saving_goals=data['saving_goals'],
                           income_expense_ratio=data['income_expense_ratio'],
                           datetime=datetime,
                           budget_message=data['budget_message'],
                           notifications=data['notifications'],
                           top_asset_categories=data['top_asset_categories'],
                           total_amount=data['total_amount'],
                           top_5_loans=data['top_5_loans'],
                           tasks=data['tasks'],
                           top_crypto_names=data['top_crypto_names'],
                           top_crypto_with_prices=data['top_crypto_with_prices'])

@views.route('/transactions')
def transactions():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    transactions = Transaction.get_all_transactions_by_user(ObjectId(user_id))
    loans = Loan.get_all_loans_by_user(ObjectId(user_id))
    print(f"Retrieved transactions for user {user_id}: {transactions}")  # Debug statement
    return render_template('transactions.html', transactions=transactions, loans=loans)

@views.route('/credit_card')
def credit_card():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    credit_card_transactions = Transaction.get_credit_card_transactions_by_user(ObjectId(user_id))
    return render_template('creditCard.html', credit_card_transactions=credit_card_transactions)


@views.route('/loan')
def loan():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    loans = Loan.get_all_loans_by_user(ObjectId(user_id))
    interest_expenses = Loan.get_total_interest_expense_by_loan(ObjectId(user_id))
    loan_expenses = Loan.get_total_loan_expense_by_loan(ObjectId(user_id))

    # Update interest_expense and loan_expense in loans based on calculated values
    for loan in loans:
        loan['interest_expense'] = interest_expenses.get(loan['name'], 0)
        loan['loan_expense'] = loan_expenses.get(loan['name'], 0)
        loan['interest_balance'] = loan['interest_payable'] - loan['interest_expense']
        loan['outstanding_balance'] = loan['original_amount'] - loan['loan_expense']
    return render_template('loan.html', loans=loans)

@views.route('/api/radar_data', methods=['GET'])
def get_radar_data():
    user_id = session['user_id']
    budget = BudgetManager.get_budget(user_id)

    if budget:
        radar_data = BudgetManager.prepare_radar_chart_data(
            user_id, 
            budget['categories'], 
            budget['budget_amounts'],
            budget['start_date'], 
            budget['end_date']
        )
        radar_data['start_date'] = budget['start_date']
        radar_data['end_date'] = budget['end_date']
    else:
        radar_data = {}

    return jsonify(radar_data)

from bson import ObjectId

@views.route('/notifications/dismiss/<notification_id>', methods=['POST'])
def dismiss_notification(notification_id):
    # notification_id = ObjectId("66ccdea30743914829c7684d")
    try:
        # Convert notification_id to ObjectId
        Notification.update_notification(ObjectId(notification_id))
        return jsonify({'success': True, 'message': 'Notification dismissed successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@views.route('/profile', methods=['GET', 'POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    user_data = current_app.mongo.cx['CE-301'].users.find_one({"_id": ObjectId(user_id)})

    if request.method == 'POST':
        username = request.form['username']
        profile_pic = request.files.get('profile_pic')

        update_data = {'username': username}

        if profile_pic and profile_pic.filename != '':
            # Check if the file is allowed
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
            def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

            if allowed_file(profile_pic.filename):
                # Generate a safe filename
                filename = secure_filename(profile_pic.filename)

                # Path to store the file, moving one level up from `src` to the root
                folder_path = os.path.join(current_app.root_path, '..', 'static/img')

                # Make sure the folder exists
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)

                # Save the file in the 'static/img/' directory
                filepath = os.path.join(folder_path, filename)
                profile_pic.save(filepath)

                # Store the filename in the user's document
                update_data['profile_pic'] = filename
            else:
                flash('Allowed image types are - png, jpg, jpeg, gif', 'error')
                return redirect(request.url)

        # Update the user in the database
        current_app.mongo.cx['CE-301'].users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )

        # Update session with the new username
        session['username'] = username

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.update_profile'))

    return render_template('profile.html', user=user_data)

def get_top_asset_categories(user_id):
    net_cash_flow = get_net_cash_flow(user_id)
    other_assets = OtherAsset.get_all_assets_by_user(user_id)

    categories = [{"name": "Net Cash Flow", "amount": net_cash_flow, "category": "Cash Flow"}]
    for asset in other_assets:
        categories.append({"name": asset['name'], "amount": asset['amount'], "category": asset.get('category', 'Other')})

    sorted_categories = sorted(categories, key=lambda x: x['amount'], reverse=True)
    top_categories = sorted_categories[:5]

    # Calculate total amount for percentage
    total_amount = sum(item['amount'] for item in top_categories)

    if not top_categories or total_amount == 0:
        # Return a message if no assets are available
        return [], 0
    
    return top_categories, total_amount

@views.route('/api/top_asset_categories', methods=['GET'])
def api_top_asset_categories():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    top_asset_categories, total_amount = get_top_asset_categories(user_id)

    # Check if no assets are available
    if not top_asset_categories or total_amount == 0:
        return jsonify({
            "message": "No assets available to display.",
            "top_asset_categories": [],
            "total_amount": 0
        }), 200
    
    return jsonify({
        "top_asset_categories": top_asset_categories,
        "total_amount": total_amount
    })

@views.route('/api/asset_allocation', methods=['GET'])
def get_asset_allocation():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    
    # Fetch individual assets
    net_cash_flow = get_net_cash_flow(user_id)
    stocks = sum(holding['amount_bought'] for holding in current_app.mongo.db.stock_holdings.find({'userId': ObjectId(user_id)}))
    crypto = sum(holding['amount_bought'] for holding in current_app.mongo.db.crypto_holdings.find({'userId': ObjectId(user_id)}))

    # Sum up only "Bonds" category from other assets, skipping assets with zero or nil amounts
    bonds = sum(
        asset['amount'] for asset in OtherAsset.get_all_assets_by_user(user_id)
        if asset.get('category') == 'Bonds' and asset.get('amount', 0) > 0
    )

    total_assets = net_cash_flow + bonds + stocks + crypto
    if total_assets == 0:
        return jsonify({"error": "No assets available"}), 200

    # Calculate user allocation percentages
    asset_allocation = [
        {"name": "Cash", "value": net_cash_flow},
        {"name": "Bonds", "value": bonds},
        {"name": "Stocks", "value": stocks},
        {"name": "Crypto", "value": crypto}
    ]
    asset_allocation = [asset for asset in asset_allocation if asset['value'] > 0]  # Filter out zero balances
    allocation_percentages = {asset['name']: (asset['value'] / total_assets) * 100 for asset in asset_allocation}

    # Define portfolio models with target percentages
    portfolio_models = {
        "Conservative": {"Bonds": 60, "Stocks": 25, "Cash": 10, "Crypto": 5},
        "Moderate": {"Bonds": 30, "Stocks": 40, "Cash": 10, "Crypto": 20},
        "Aggressive": {"Bonds": 20, "Stocks": 50, "Cash": 5, "Crypto": 25}
    }

    # Calculate the difference score for each portfolio
    def calculate_difference(target, actual):
        return sum(abs(target.get(asset, 0) - actual.get(asset, 0)) for asset in target)

    # Find the closest portfolio match based on minimum difference score
    best_match = min(portfolio_models, key=lambda model: calculate_difference(portfolio_models[model], allocation_percentages))
    
    # Return asset allocation and the best matching portfolio type
    return jsonify({
        "asset_allocation": asset_allocation,
        "portfolio_type": best_match
    })


