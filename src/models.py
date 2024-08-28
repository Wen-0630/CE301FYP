from flask import current_app
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import pytz
from .notifications import send_saving_goal_notification

class Transaction:
    def __init__(self, userId, type, category, amount, date, description, payment_method=None, repayment_status='Pending',loan_name=None):
        self.userId = ObjectId(userId) if isinstance(userId, str) else userId
        self.type = type
        self.category = category
        self.amount = amount
        self.date = date
        self.description = description
        self.payment_method = payment_method
        self.remaining_amount = amount  # Initialize remaining amount with the transaction amount
        self.repayment_status = repayment_status  # Initialize repayment status with default value
        self.loan_name = loan_name if loan_name else None

    def save(self):
        transaction = {
            'userId': self.userId,
            'type': self.type,
            'category': self.category,
            'amount': self.amount,
            'date': self.date,
            'description': self.description,
            'payment_method': self.payment_method,
            'remaining_amount': self.remaining_amount,  # Save remaining amount
            'repayment_status': self.repayment_status,  # Save repayment status
            'loan_name': self.loan_name
        }
        result = current_app.mongo.db.transactions.insert_one(transaction)
        return result
    
    @staticmethod
    def get_all_transactions_by_user(userId):
        # Ensure userId is an ObjectId
        userId = ObjectId(userId) if isinstance(userId, str) else userId
        transactions = list(current_app.mongo.db.transactions.find({'userId': userId}))
        print(f"get_all_transactions_by_user - Retrieved transactions: {transactions}")  # Debug statement
        return transactions

    @staticmethod
    def get_transaction(transaction_id):
        transaction = current_app.mongo.db.transactions.find_one({'_id': ObjectId(transaction_id)})
        print(f"get_transaction - Retrieved transaction: {transaction}")  # Debug statement
        return transaction

    @staticmethod
    def update_transaction(transaction_id, data):
        print(f"update_transaction - Updating transaction {transaction_id} with data: {data}")  # Debug statement
        current_app.mongo.db.transactions.update_one({'_id': ObjectId(transaction_id)}, {"$set": data})

    @staticmethod
    def delete_transaction(transaction_id):
        print(f"delete_transaction - Deleting transaction with ID: {transaction_id}")  # Debug statement
        current_app.mongo.db.transactions.delete_one({'_id': ObjectId(transaction_id)})

    @staticmethod
    def get_credit_card_transactions_by_user(userId):
        userId = ObjectId(userId) if isinstance(userId, str) else userId
        return list(current_app.mongo.db.transactions.find({'userId': userId, 'payment_method': 'Credit Card'}))

# models.py
class Repayment:
    @staticmethod
    def add_repayment(transaction_id, repayment_amount, repayment_date):
        repayment = {
            'transaction_id': ObjectId(transaction_id),
            'repayment_amount': repayment_amount,
            'repayment_date': repayment_date
        }
        result = current_app.mongo.db.repayments.insert_one(repayment)
        return result

    @staticmethod
    def get_repayments_by_transaction(transaction_id):
        return list(current_app.mongo.db.repayments.find({'transaction_id': ObjectId(transaction_id)}))
    
    @staticmethod
    def get_repayment(repayment_id):
        return current_app.mongo.db.repayments.find_one({'_id': ObjectId(repayment_id)})

    @staticmethod
    def delete_repayment(repayment_id):
        current_app.mongo.db.repayments.delete_one({'_id': ObjectId(repayment_id)})

    @staticmethod
    def get_total_repayment_amount(transaction_id):
        total_repayment = current_app.mongo.db.repayments.aggregate([
            {"$match": {"transaction_id": ObjectId(transaction_id)}},
            {"$group": {"_id": None, "total": {"$sum": "$repayment_amount"}}}
        ])
        result = list(total_repayment)
        if result:
            return result[0]['total']
        return 0


# src/models.py
class Loan:
    def __init__(self, userId, name, loan_type, original_amount, loan_term, repayment_term, interest_rate, outstanding_balance, interest_payable, interest_expense, loan_expense, issue_date, maturity_date, description=None):
        self.userId = ObjectId(userId) if isinstance(userId, str) else userId
        self.name = name
        self.loan_type = loan_type
        self.original_amount = original_amount
        self.loan_term = loan_term
        self.repayment_term = repayment_term
        self.interest_rate = interest_rate
        self.outstanding_balance = outstanding_balance
        self.interest_payable = interest_payable
        self.interest_expense = interest_expense
        self.loan_expense = loan_expense
        self.interest_balance = self.calculate_interest_balance()
        self.outstanding_balance = self.calculate_outstanding_balance()
        self.issue_date = issue_date
        self.maturity_date = maturity_date
        self.description = description

    def calculate_interest_balance(self):
        return self.interest_payable - self.interest_expense
    
    def calculate_outstanding_balance(self):
        return self.original_amount - self.loan_expense

    def save(self):
        loan = {
            'userId': self.userId,
            'name': self.name,
            'loan_type': self.loan_type,
            'original_amount': self.original_amount,
            'loan_term': self.loan_term,
            'repayment_term': self.repayment_term,
            'interest_rate': self.interest_rate,
            'outstanding_balance': self.outstanding_balance,
            'interest_payable': self.interest_payable,
            'interest_expense': self.interest_expense,
            'interest_balance': self.calculate_interest_balance(),
            'outstanding_balance': self.calculate_outstanding_balance(),
            'loan_expense': self.loan_expense,
            'issue_date': self.issue_date,
            'maturity_date': self.maturity_date,
            'description': self.description
        }
        result = current_app.mongo.db.loans.insert_one(loan)
        return result

    @staticmethod
    def get_all_loans_by_user(userId):
        userId = ObjectId(userId) if isinstance(userId, str) else userId
        loans = list(current_app.mongo.db.loans.find({'userId': userId}))
        return loans

    @staticmethod
    def get_loan(loan_id):
        loan = current_app.mongo.db.loans.find_one({'_id': ObjectId(loan_id)})
        return loan

    @staticmethod
    def update_loan(loan_id, data):
        if 'interest_payable' in data and 'interest_expense' in data:
            data['interest_balance'] = data['interest_payable'] - data['interest_expense']
        if 'original_amount' in data and 'loan_expense' in data:
            data['outstanding_balance'] = data['original_amount'] - data['loan_expense']
        current_app.mongo.db.loans.update_one({'_id': ObjectId(loan_id)}, {"$set": data})

    @staticmethod
    def delete_loan(loan_id):
        current_app.mongo.db.loans.delete_one({'_id': ObjectId(loan_id)})
    
    @staticmethod
    def get_loan_by_name(name, userId):
        userId = ObjectId(userId) if isinstance(userId, str) else userId
        loan = current_app.mongo.db.loans.find_one({'name': name, 'userId': userId})
        return loan

    @staticmethod
    def update_interest_expense(loan_name, user_id):
        transactions = current_app.mongo.db.transactions.find({'loan_name': loan_name, 'userId': ObjectId(user_id), 'category': 'Interest Expense'})
        total_interest_expense = sum(transaction['amount'] for transaction in transactions)
        current_app.mongo.db.loans.update_one({'name': loan_name, 'userId': ObjectId(user_id)}, {"$set": {'interest_expense': total_interest_expense}})

    @staticmethod
    def get_total_interest_expense_by_loan(user_id):
        pipeline = [
            {"$match": {"userId": ObjectId(user_id), "category": "Interest Expense"}},
            {"$group": {"_id": "$loan_name", "total_interest_expense": {"$sum": "$amount"}}}
        ]
        result = list(current_app.mongo.db.transactions.aggregate(pipeline))
        return {item['_id']: item['total_interest_expense'] for item in result}

    @staticmethod
    def update_loan_expense(loan_name, user_id):
        transactions = current_app.mongo.db.transactions.find({'loan_name': loan_name, 'userId': ObjectId(user_id), 'category': 'Loan Expense'})
        total_loan_expense = sum(transaction['amount'] for transaction in transactions)
        current_app.mongo.db.loans.update_one({'name': loan_name, 'userId': ObjectId(user_id)}, {"$set": {'loan_expense': total_loan_expense}})

    @staticmethod
    def get_total_loan_expense_by_loan(user_id):
        pipeline = [
            {"$match": {"userId": ObjectId(user_id), "category": "Loan Expense"}},
            {"$group": {"_id": "$loan_name", "total_loan_expense": {"$sum": "$amount"}}}
        ]
        result = list(current_app.mongo.db.transactions.aggregate(pipeline))
        return {item['_id']: item['total_loan_expense'] for item in result}

class SavingGoal:
    def __init__(self, user_id, name, target_amount=None, target_date=None, current_amount=0, is_active=True, is_automatic=False):
        self.user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        self.name = name
        self.target_amount = target_amount
        self.current_amount = current_amount
        self.creation_date = datetime.utcnow()
        self.target_date = target_date
        self.is_active = is_active
        self.is_automatic = is_automatic

    def save(self):
        goal = {
            'user_id': self.user_id,
            'name': self.name,
            'target_amount': self.target_amount,
            'current_amount': self.current_amount,
            'creation_date': self.creation_date,
            'target_date': self.target_date,
            'is_active': self.is_active,
            'is_automatic': self.is_automatic
        }
        result = current_app.mongo.db.saving_goals.insert_one(goal)
        return result.inserted_id

    @staticmethod
    def deactivate_current_goal(user_id):
        current_app.mongo.db.saving_goals.update_many(
            {'user_id': ObjectId(user_id), 'is_active': True},
            {'$set': {'is_active': False}}
        )
    
    @staticmethod
    def get_active_goal(user_id):
        user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        return current_app.mongo.db.saving_goals.find_one({'user_id': user_id, 'is_active': True})
    
    @staticmethod
    def get_goal_history(user_id):
        user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        return list(current_app.mongo.db.saving_goals.find({'user_id': user_id}).sort('creation_date', -1))

    
    @staticmethod
    def get_goal(goal_id):
        return current_app.mongo.db.saving_goals.find_one({'_id': ObjectId(goal_id)})

    @staticmethod
    def get_goals_by_user(user_id):
        user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        return list(current_app.mongo.db.saving_goals.find({'user_id': user_id, 'is_active': True}))
    
    @staticmethod
    def update_goal(goal_id, data):
        current_app.mongo.db.saving_goals.update_one({'_id': ObjectId(goal_id)}, {"$set": data})

    
    @staticmethod
    def delete_goal(goal_id):
        current_app.mongo.db.saving_goals.delete_one({'_id': ObjectId(goal_id)})

    @staticmethod
    def calculate_current_amount(goal_id, user_id):
        goal = SavingGoal.get_goal(goal_id)
        if not goal:
            return 0
        
        # Calculate net income (Income - Expenses) since the creation of the goal until the target date
        user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        creation_date = goal['creation_date']
        target_date = goal['target_date']

        # Aggregate income
        income_pipeline = [
            {"$match": {
                "userId": user_id,
                "date": {"$gte": creation_date, "$lte": target_date},
                "type": "Income"
            }},
            {"$group": {"_id": None, "total_income": {"$sum": "$amount"}}}
        ]
        income_result = list(current_app.mongo.db.transactions.aggregate(income_pipeline))
        total_income = income_result[0]['total_income'] if income_result else 0

        # Aggregate expenses
        expense_pipeline = [
            {"$match": {
                "userId": user_id,
                "date": {"$gte": creation_date, "$lte": target_date},
                "type": "Expense"
            }},
            {"$group": {"_id": None, "total_expense": {"$sum": "$amount"}}}
        ]
        expense_result = list(current_app.mongo.db.transactions.aggregate(expense_pipeline))
        total_expense = expense_result[0]['total_expense'] if expense_result else 0

        # Calculate net income
        net_income = total_income - total_expense

        # Ensure the current amount is not negative
        current_amount = max(0, net_income)

        # Check if the current amount meets or exceeds the target amount before updating
        if current_amount >= goal.get('target_amount', float('inf')):
        # Trigger the goal achieved notification
            send_saving_goal_notification(goal['user_id'], goal['name'])

        # Update the current amount in the saving goal
        SavingGoal.update_goal(goal_id, {"current_amount": current_amount})

        return current_amount
    
    # @staticmethod
    # def update_current_amount_in_db(goal_id, user_id):
    #     """Calculates the current amount and updates it in the database."""
    #     # Ensure goal_id and user_id are ObjectIds
    #     goal_id = ObjectId(goal_id) if not isinstance(goal_id, ObjectId) else goal_id
    #     user_id = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
        
    #     current_amount = SavingGoal.calculate_current_amount('_id', user_id)
    #     SavingGoal.update_goal(goal_id, {"current_amount": current_amount})
    #     return current_amount

    
    @staticmethod
    def calculate_automatic_target_amount(user_id):
        # Get the current UTC datetime
        current_date = datetime.utcnow()

        # Get the first and last day of the current month
        start_date = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.UTC)
        if current_date.month == 12:
            end_date = current_date.replace(year=current_date.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.UTC)
        else:
            end_date = current_date.replace(month=current_date.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.UTC)

        # Ensure userId is an ObjectId
        user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id

        # Debugging print to check start_date and end_date
        print(f"Start Date: {start_date.isoformat()}, End Date: {end_date.isoformat()}")

        # MongoDB query to match transactions in the current month
        income_pipeline = [
            {"$match": {
                "userId": user_id,
                "type": "Income",
                "date": {"$gte": start_date, "$lt": end_date}
            }},
            {"$group": {"_id": None, "total_income": {"$sum": "$amount"}}}
        ]

        # Execute the pipeline and capture the result
        income_result = list(current_app.mongo.db.transactions.aggregate(income_pipeline))

        # Debugging output to verify the pipeline result
        print("Income Pipeline Results:", income_result)

        # Calculate total income and return 20% of it
        total_income = income_result[0]['total_income'] if income_result else 0
        return total_income * 0.2

    @staticmethod
    def calculate_automatic_current_amount(user_id):
        current_date = datetime.utcnow()
        current_month = current_date.month
        year = current_date.year

        # Calculate total income
        income_pipeline = [
            {"$match": {
                "userId": user_id,
                "type": "Income",
                "date": {"$gte": datetime(year, current_month, 1), "$lt": datetime(year, current_month + 1, 1)}
            }},
            {"$group": {"_id": None, "total_income": {"$sum": "$amount"}}}
        ]
        income_result = list(current_app.mongo.db.transactions.aggregate(income_pipeline))
        total_income = income_result[0]['total_income'] if income_result else 0

        # Calculate total expense
        expense_pipeline = [
            {"$match": {
                "userId": user_id,
                "type": "Expense",
                "date": {"$gte": datetime(year, current_month, 1), "$lt": datetime(year, current_month + 1, 1)}
            }},
            {"$group": {"_id": None, "total_expense": {"$sum": "$amount"}}}
        ]
        expense_result = list(current_app.mongo.db.transactions.aggregate(expense_pipeline))
        total_expense = expense_result[0]['total_expense'] if expense_result else 0

        # Calculate net income
        return max(0, total_income - total_expense)


    @staticmethod
    def set_automatic_target_date():
        now = datetime.utcnow()  # Use datetime.utcnow() directly
        first_of_next_month = datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)
        last_day_of_current_month = first_of_next_month - timedelta(days=1)
        return last_day_of_current_month
    
class Budget:
    def __init__(self, userId, start_date, end_date, categories, budget_amounts=None):
        self.userId = ObjectId(userId) if isinstance(userId, str) else userId
        self.start_date = start_date
        self.end_date = end_date
        self.categories = categories
        self.budget_amounts = budget_amounts or {}
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'userId': self.userId,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'categories': self.categories,
            'budget_amounts': self.budget_amounts,
            'created_at': self.created_at
        }

    def save(self):
        budget_data = self.to_dict()
        result = current_app.mongo.db.budgets.insert_one(budget_data)
        return result

    @staticmethod
    def get_latest_budget_by_user(userId):
        userId = ObjectId(userId) if isinstance(userId, str) else userId
        budget = current_app.mongo.db.budgets.find({'userId': userId}).sort('created_at', -1).limit(1)
        return budget[0] if budget else None

    @staticmethod
    def get_budget_by_user_and_date(userId, start_date, end_date):
        userId = ObjectId(userId) if isinstance(userId, str) else userId
        budget = current_app.mongo.db.budgets.find_one({
            'userId': userId,
            'start_date': {'$lte': start_date},
            'end_date': {'$gte': end_date}
        })
        return budget

    @staticmethod
    def update_budget(budget_id, data):
        current_app.mongo.db.budgets.update_one({'_id': ObjectId(budget_id)}, {"$set": data})

    @staticmethod
    def delete_budget(budget_id):
        current_app.mongo.db.budgets.delete_one({'_id': ObjectId(budget_id)})

