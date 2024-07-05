from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from datetime import datetime
import pytz
from bson import ObjectId

# Notes:
# 1. Replace <username>, <password>, and <xxxxxx> with your actual MongoDB Atlas credentials and cluster URL.
# 2. Ensure flask_bcrypt and pytz are installed for password hashing and timezone support:
#    pip install flask_bcrypt pytz
# 3. Run the populateDB.py script:
#    python populateDB.py

# MongoDB connection string
MONGO_URI = "mongodb+srv://<username>:<password>@database.<xxxxxx>.mongodb.net/CE-301?retryWrites=true&w=majority&appName=Database"
client = MongoClient(MONGO_URI)

# Initialize Bcrypt
bcrypt = Bcrypt()

# Database and collections
db = client.Database
users_col = db.users
cash_flow_col = db.cash_flow
crypto_holdings_col = db.crypto_holdings
loans_col = db.loans
repayments_col = db.repayments
transactions_col = db.transactions

# Sample data to be inserted
users_data = [
    {"_id": ObjectId("6649031375224af8fe919c45"), 
     "username": "Jason", 
     "email": "jason2@gmail.com", 
     "password": bcrypt.generate_password_hash("password").decode('utf-8')}
]

cash_flow_data = [
    {"_id": ObjectId("6686d041e02e81e916deb494"), 
     "userId": ObjectId("6649031375224af8fe919c45"), 
     "initial_cash": 7000}
]

crypto_holdings_data = [
    {
        "_id": ObjectId("6686c7d32ecded0dbb0a4b9"), 
        "userId": ObjectId("6649031375224af8fe919c45"), 
        "asset": "ethereum", 
        "buy_price": 100, 
        "amount_bought": 1000, 
        "quantity": 10, 
        "transaction_fee": 0, 
        "deduct_cash": "Yes", 
        "type": "crypto", 
        "profit_loss": 30314.699999999997, 
        "datetime": datetime(2024, 7, 1, 12, 0, 0, tzinfo=pytz.UTC)
    },
    {
        "_id": ObjectId("6686c7d32ecded0dbb0a4b9"), 
        "userId": ObjectId("6649031375224af8fe919c45"), 
        "asset": "ethereum", 
        "buy_price": 100, 
        "amount_bought": 1000, 
        "quantity": 10, 
        "transaction_fee": 0, 
        "deduct_cash": "Yes", 
        "type": "crypto", 
        "profit_loss": 30314.699999999997, 
        "datetime": datetime(2024, 7, 1, 12, 0, 0, tzinfo=pytz.UTC)
    }
]

loans_data = [
    {"_id": ObjectId("6673094f78723b49272d045d"), 
     "userId": ObjectId("6649031375224af8fe919c45"), 
     "loan_type": "Personal Loan", 
     "original_amount": 10000, 
     "loan_term": 12, 
     "repayment_term": "Monthly", 
     "interest_rate": 3.5, 
     "outstanding_balance": 8500, 
     "interest_payable": 350, 
     "interest_expense": 150, 
     "interest_balance": 200, 
     "loan_expense": 1500, 
     "issue_date": datetime(2024, 6, 20, tzinfo=pytz.UTC), 
     "maturity_date": datetime(2025, 6, 20, tzinfo=pytz.UTC), 
     "description": "Loan from DBS", "name": "Loan 1"}
]

repayments_data = [
    {"_id": ObjectId("6686fc8131b5e0f9481a8684"), 
     "transaction_id": ObjectId("6686f653dc1f359210e3593c"), 
     "repayment_amount": 100, 
     "repayment_date": datetime(2024, 7, 4, tzinfo=pytz.UTC)}
]

transactions_data = [
    {
        "_id": ObjectId("6675e37e349d5ccf3dd81ca7"), 
        "userId": ObjectId("6649031375224af8fe919c45"), 
        "type": "Expense", 
        "category": "Interest Expense", 
        "amount": 100, 
        "date": datetime(2024, 6, 22, tzinfo=pytz.UTC), 
        "description": "test2", 
        "payment_method": "Cash", 
        "repayment_status": "Pending", 
        "loan_name": "Loan 1"
    },
    {
        "_id": ObjectId("6675e4a7feb0727f4421f3a7"), 
        "userId": ObjectId("6649031375224af8fe919c45"), 
        "type": "Expense", 
        "category": "Loan Expense", 
        "amount": 1000, 
        "date": datetime(2024, 6, 22, tzinfo=pytz.UTC), 
        "description": "test", 
        "payment_method": "Cash", 
        "repayment_status": "Pending", 
        "loan_name": "Loan 1"
    },
    {
        "_id": ObjectId("6675e4e0feb0727f4421f3a8"), 
        "userId": ObjectId("6649031375224af8fe919c45"), 
        "type": "Expense", 
        "category": "Loan Expense", 
        "amount": 500, 
        "date": datetime(2024, 6, 22, tzinfo=pytz.UTC), 
        "description": "test2", 
        "payment_method": "Cash", 
        "repayment_status": "Pending", 
        "loan_name": "Loan 1"
    },
    {
        "_id": ObjectId("6686ef96cbeabd572e2186c4"), 
        "userId": ObjectId("6649031375224af8fe919c45"), 
        "type": "Expense", 
        "category": "Interest Expense", 
        "amount": 50, 
        "date": datetime(2024, 7, 3, tzinfo=pytz.UTC), 
        "description": "test", 
        "payment_method": "Bank Transfer", 
        "remaining_amount": 50, 
        "repayment_status": "Pending", 
        "loan_name": "Loan 1"
    },
    {
        "_id": ObjectId("6686f653dc1f359210e3593c"), 
        "userId": ObjectId("6649031375224af8fe919c45"), 
        "type": "Expense", 
        "category": "Shopping", 
        "amount": 10000, 
        "date": datetime(2024, 7, 1, tzinfo=pytz.UTC), 
        "description": "bag", 
        "payment_method": "Credit Card", 
        "remaining_amount": 9900, 
        "repayment_status": "Pending", 
        "repayment_date": datetime(2024, 7, 4, tzinfo=pytz.UTC)
    }
]

# Insert data into collections
users_col.insert_many(users_data)
cash_flow_col.insert_many(cash_flow_data)
crypto_holdings_col.insert_many(crypto_holdings_data)
loans_col.insert_many(loans_data)
repayments_col.insert_many(repayments_data)
transactions_col.insert_many(transactions_data)

print("All data inserted successfully!")
