from bson.objectid import ObjectId
from flask import current_app, Blueprint, request, redirect, url_for, session, flash
from datetime import datetime
from .models import Budget

# Define the Blueprint
budget_bp = Blueprint('budget', __name__)

class BudgetManager:
    @staticmethod
    def validate_budget(categories, budget_amounts):
        """
        Validates that the budget has between 3 to 6 non-zero categories.
        """
        filled_categories = [amount for amount in budget_amounts.values() if amount > 0]
        if len(filled_categories) < 3 or len(filled_categories) > 6:
            return False
        return True
    
    @staticmethod
    def get_filtered_expenses(user_id, categories, start_date, end_date):
        user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        pipeline = [
            {"$match": {
                "userId": user_id,
                "type": "Expense",
                "category": {"$in": categories},
                "date": {"$gte": start_date, "$lte": end_date}
            }},
            {"$group": {
                "_id": "$category",
                "total_amount": {"$sum": "$amount"}
            }}
        ]

        expenses = list(current_app.mongo.db.transactions.aggregate(pipeline))
        return expenses

    @staticmethod
    def prepare_radar_chart_data(user_id, categories, budget_amounts, start_date, end_date):
        expenses = BudgetManager.get_filtered_expenses(user_id, categories, start_date, end_date)

        radar_data = {
            "indicators": [],
            "budget_values": [],
            "actual_values": []
        }

        expense_map = {exp['_id']: exp['total_amount'] for exp in expenses}

        for category in categories:
            budget_amount = budget_amounts.get(category, 0)
            if budget_amount > 0:
                radar_data["indicators"].append({"text": category, "max": budget_amount})
                radar_data["budget_values"].append(budget_amount)
                radar_data["actual_values"].append(expense_map.get(category, 0))

        return radar_data

    @staticmethod
    def get_latest_budget(user_id):
        budget = Budget.get_latest_budget_by_user(user_id)
        return budget

    @staticmethod
    def get_budget(user_id):
        return BudgetManager.get_latest_budget(user_id)

@budget_bp.route('/save_budget', methods=['POST'])
def save_budget():
    user_id = session['user_id']
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    categories = ['Food', 'Shopping', 'Transport', 'Interest Expense', 'Loan Expense', 'Other']
    budget_amounts = {}

    # Count the number of non-zero budget categories
    non_zero_categories_count = 0

    for category in categories:
        budget_value = request.form.get(f'budget_{category}')
        if budget_value is not None:
            try:
                budget_amount = float(budget_value)
                if budget_amount > 0:
                    non_zero_categories_count += 1
                budget_amounts[category] = budget_amount
            except ValueError:
                budget_amounts[category] = 0.0  # Default to 0 if parsing fails or empty

    # Validate the number of non-zero budget categories
    if non_zero_categories_count < 3 or non_zero_categories_count > 6:
        flash('Please input budget amounts for at least 3 and no more than 6 categories.', 'error')
        return redirect(url_for('user.dashboard'))

    # Create and save the Budget object
    budget = Budget(userId=user_id, start_date=start_date, end_date=end_date, categories=categories, budget_amounts=budget_amounts)
    budget.save()

    flash('Budget saved successfully!', 'success')
    return redirect(url_for('user.dashboard'))
