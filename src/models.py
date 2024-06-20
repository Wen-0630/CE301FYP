from flask import current_app
from bson.objectid import ObjectId
import datetime

class Transaction:
    def __init__(self, userId, type, category, amount, date, description, payment_method=None, repayment_status='Pending'):
        self.userId = ObjectId(userId) if isinstance(userId, str) else userId
        self.type = type
        self.category = category
        self.amount = amount
        self.date = date
        self.description = description
        self.payment_method = payment_method
        self.remaining_amount = amount  # Initialize remaining amount with the transaction amount
        self.repayment_status = repayment_status  # Initialize repayment status with default value

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
            'repayment_status': self.repayment_status  # Save repayment status
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
# class CreditCard:
#     def __init__(self, userId, type, name, value, date):
#         self.userId = ObjectId(userId)
#         self.type = type
#         self.name = name
#         self.value = value
#         self.date = date

#     def save(self):
#         credit_card = {
#             'userId': self.userId,
#             'type': self.type,
#             'name': self.name,
#             'value': self.value,
#             'date': self.date,
#         }
#         return current_app.mongo.db.credit_cards.insert_one(credit_card) 

#     @staticmethod
#     def get_all_credit_cards_by_user(userId):
#         userId = ObjectId(userId)
#         return list(current_app.mongo.db.credit_cards.find({'userId': userId}))  


# src/models.py
class Loan:
    def __init__(self, userId, name, loan_type, original_amount, loan_term, repayment_term, interest_rate, outstanding_balance, interest_payable, interest_expense, interest_balance, loan_expense, issue_date, maturity_date, description=None):
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
        self.interest_balance = interest_balance
        self.loan_expense = loan_expense
        self.issue_date = issue_date
        self.maturity_date = maturity_date
        self.description = description

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
            'interest_balance': self.interest_balance,
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
        current_app.mongo.db.loans.update_one({'_id': ObjectId(loan_id)}, {"$set": data})

    @staticmethod
    def delete_loan(loan_id):
        current_app.mongo.db.loans.delete_one({'_id': ObjectId(loan_id)})
