from flask import current_app
from bson.objectid import ObjectId
import datetime

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
        self.interest_balance = self.calculate_interest_balance()
        self.outstanding_balance = self.calculate_outstanding_balance()
        self.loan_expense = loan_expense
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
