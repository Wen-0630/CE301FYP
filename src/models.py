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
