from flask import current_app
from bson.objectid import ObjectId
import datetime

class Transaction:
    def __init__(self, userId, type, category, amount, date, description):
        # Ensure userId is stored as an ObjectId
        self.userId = ObjectId(userId) if isinstance(userId, str) else userId
        self.type = type
        self.category = category
        self.amount = amount
        self.date = date
        self.description = description

    def save(self):
        transaction = {
            'userId': self.userId,
            'type': self.type,
            'category': self.category,
            'amount': self.amount,
            'date': self.date,
            'description': self.description
        }
        result = current_app.mongo.db.transactions.insert_one(transaction)
        print(f"save - Inserted transaction ID: {result.inserted_id}")  # Debug statement
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

