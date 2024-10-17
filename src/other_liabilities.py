from flask import Blueprint, request, jsonify, session, current_app,redirect,render_template,url_for
from bson.objectid import ObjectId
from datetime import datetime

# Define a new Blueprint for other liabilities
other_liabilities = Blueprint('other_liabilities', __name__)

class OtherLiability:
    def __init__(self, user_id, name, amount, description=None, category=None):
        self.user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        self.name = name
        self.amount = amount
        self.date_added = datetime.utcnow()
        self.description = description
        self.category = category

    def save(self):
        liability = {
            'user_id': self.user_id,
            'name': self.name,
            'amount': self.amount,
            'date_added': self.date_added,
            'description': self.description,
            'category': self.category
        }
        result = current_app.mongo.db.other_liabilities.insert_one(liability)
        return result.inserted_id

    @staticmethod
    def get_all_liabilities_by_user(user_id):
        user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        return list(current_app.mongo.db.other_liabilities.find({'user_id': user_id}))

    @staticmethod
    def get_total_other_liabilities(user_id):
        user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        result = current_app.mongo.db.other_liabilities.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "total_amount": {"$sum": "$amount"}}}
        ])
        total = list(result)
        return total[0]['total_amount'] if total else 0

    @staticmethod
    def delete_liability(liability_id):
        current_app.mongo.db.other_liabilities.delete_one({'_id': ObjectId(liability_id)})

    @staticmethod
    def get_liability_by_id(liability_id):
        return current_app.mongo.db.other_liabilities.find_one({'_id': ObjectId(liability_id)})

    @staticmethod
    def update_liability(liability_id, update_data):
        current_app.mongo.db.other_liabilities.update_one(
            {'_id': ObjectId(liability_id)},
            {'$set': update_data}
        )

# Route to view all liabilities
@other_liabilities.route('/other_liabilities', methods=['GET'])
def view_other_liabilities():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    liabilities = OtherLiability.get_all_liabilities_by_user(user_id)
    return render_template('other_liabilities.html', liabilities=liabilities)

# Route to add a new liability
@other_liabilities.route('/other_liabilities/add', methods=['POST'])
def add_other_liability():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    name = request.form.get('name')
    amount = float(request.form.get('amount'))
    description = request.form.get('description', '')
    category = request.form.get('category', '')

    liability = OtherLiability(user_id, name, amount, description, category)
    liability.save()

    return redirect(url_for('other_liabilities.view_other_liabilities'))

# Route to delete a liability
@other_liabilities.route('/other_liabilities/delete/<liability_id>', methods=['POST'])
def delete_liability(liability_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    OtherLiability.delete_liability(liability_id)
    return redirect(url_for('other_liabilities.other_liabilities'))

# Route to edit a liability (GET and POST)
@other_liabilities.route('/other_liabilities/edit/<liability_id>', methods=['GET', 'POST'])
def edit_other_liability(liability_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    if request.method == 'POST':
        update_data = {
            'name': request.form.get('name'),
            'amount': float(request.form.get('amount')),
            'category': request.form.get('category', ''),
            'description': request.form.get('description', '')
        }
        OtherLiability.update_liability(liability_id, update_data)
        return redirect(url_for('other_liabilities.view_other_liabilities'))

    liability = OtherLiability.get_liability_by_id(liability_id)
    return render_template('edit_other_liability.html', liability=liability)
