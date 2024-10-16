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
import datetime 
import json
import os

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
    user = current_app.mongo.cx['CE-301'].users.find_one({"_id": ObjectId(user_id)})
    if 'profile_pic' not in user:
        user['profile_pic'] = 'default_profile.png'

    total_income = calculate_total_income(user_id)
    total_expense = calculate_total_expense(user_id)
    total_credit_card_outstanding = get_total_outstanding(user_id)

    loans = Loan.get_all_loans_by_user(ObjectId(user_id))
    total_loan_outstanding = sum(loan['outstanding_balance'] + loan['interest_balance'] for loan in loans)
    
    total_outstanding = total_credit_card_outstanding + total_loan_outstanding

    total_investment = calculate_total_investment_profit_loss(user_id)

    net_cash_flow = get_net_cash_flow(user_id)
    total_other_assets = OtherAsset.get_total_other_assets(user_id)
    total_assets = net_cash_flow + total_other_assets

    net_worth = total_assets + total_investment - total_outstanding

    saving_goals = SavingGoal.get_goals_by_user(user_id)
    for goal in saving_goals:
        # Update the current amount before rendering the dashboard
        SavingGoal.calculate_current_amount(goal['_id'], user_id)

    if total_expense > 0:
        income_expense_ratio = round((total_expense / total_income) * 100, 2)
    elif total_income > 0:
        income_expense_ratio = 0.00  # Set the ratio to 0 if income exists but expense is nil
    else:
        income_expense_ratio = 100.00

    send_income_expense_ratio_notification(user_id, income_expense_ratio)

    budget = BudgetManager.get_latest_budget(user_id)

    if budget:
        radar_data = BudgetManager.prepare_radar_chart_data(
            user_id, 
            budget['categories'], 
            budget['budget_amounts'], 
            budget['start_date'], 
            budget['end_date']
        )
        send_budget_vs_spending_notification(user_id, radar_data)
        radar_data_json = json.dumps(radar_data)
        budget_message = ""
    else:
        radar_data = "{}"
        budget_message = "No active budget. Please set a budget."

    # radar_data_json = json.dumps(radar_data)

    notifications = Notification.get_active_notifications(user_id)

    return render_template('dashboard.html', 
                           user=user,
                           total_income=total_income, 
                           total_expense=total_expense, 
                           total_outstanding=total_outstanding, 
                           total_investment=total_investment, 
                           total_assets=total_assets,
                           net_worth=net_worth,
                           saving_goals=saving_goals,
                           income_expense_ratio=income_expense_ratio,
                           datetime=datetime,
                           budget_message=budget_message,
                           notifications=notifications)

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


