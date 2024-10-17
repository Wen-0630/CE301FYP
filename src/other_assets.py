from flask import Blueprint, request, jsonify, session, current_app,render_template,flash,redirect,url_for
from bson.objectid import ObjectId
from datetime import datetime

# Define a new Blueprint for other assets
other_assets = Blueprint('other_assets', __name__)

class OtherAsset:
    def __init__(self, user_id, name, amount, description=None, category=None):
        self.user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        self.name = name
        self.amount = amount
        self.date_added = datetime.utcnow()
        self.description = description
        self.category = category

    def save(self):
        asset = {
            'user_id': self.user_id,
            'name': self.name,
            'amount': self.amount,
            'date_added': self.date_added,
            'description': self.description,
            'category': self.category
        }
        result = current_app.mongo.db.other_assets.insert_one(asset)
        return result.inserted_id

    @staticmethod
    def get_all_assets_by_user(user_id):
        user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        return list(current_app.mongo.db.other_assets.find({'user_id': user_id}))

    @staticmethod
    def get_total_other_assets(user_id):
        user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        result = current_app.mongo.db.other_assets.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "total_amount": {"$sum": "$amount"}}}
        ])
        total = list(result)
        return total[0]['total_amount'] if total else 0

    @staticmethod
    def delete_asset(asset_id):
        current_app.mongo.db.other_assets.delete_one({'_id': ObjectId(asset_id)})

    @staticmethod
    def get_asset_by_id(asset_id, user_id):
        return current_app.mongo.db.other_assets.find_one({'_id': ObjectId(asset_id), 'user_id': ObjectId(user_id)})

    @staticmethod
    def update_asset(asset_id, user_id, name, amount, description, category):
        current_app.mongo.db.other_assets.update_one(
            {'_id': ObjectId(asset_id), 'user_id': ObjectId(user_id)},
            {'$set': {
                'name': name,
                'amount': amount,
                'description': description,
                'category': category
            }}
        )

# Route to handle adding a new asset
@other_assets.route('/other_assets/add', methods=['GET', 'POST'])
def add_other_asset():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    name = request.form.get('name')
    amount = float(request.form.get('amount'))
    description = request.form.get('description', '')
    category = request.form.get('category', '')

    asset = OtherAsset(user_id, name, amount, description, category)
    asset.save()

    flash('Asset added successfully!', 'success')
    return redirect(url_for('other_assets.view_other_assets'))


# Route to get total assets (other + net cash flow)
@other_assets.route('/other_assets/total', methods=['GET'])
def get_total_other_assets_route():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    total_other_assets = OtherAsset.get_total_other_assets(user_id)
    return jsonify({'total_other_assets': total_other_assets})

@other_assets.route('/other_assets', methods=['GET'])
def view_other_assets():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    assets = OtherAsset.get_all_assets_by_user(user_id)
    return render_template('other_assets.html', assets=assets)

@other_assets.route('/other_assets/edit/<asset_id>', methods=['GET', 'POST'])
def edit_other_asset(asset_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    if request.method == 'POST':
        # Get the updated asset details from the form
        name = request.form.get('name')
        amount = float(request.form.get('amount'))
        description = request.form.get('description', '')
        category = request.form.get('category', '')

        # Update the asset in the database
        OtherAsset.update_asset(asset_id, user_id, name, amount, description, category)

        flash('Asset updated successfully!', 'success')
        return redirect(url_for('other_assets.view_other_assets'))

    # If it's a GET request, fetch the asset's current details
    asset = OtherAsset.get_asset_by_id(asset_id, user_id)

    if not asset:
        flash('Asset not found', 'error')
        return redirect(url_for('other_assets.other_assets'))

    return render_template('edit_other_asset.html', asset=asset)

# Route to handle deleting an asset
@other_assets.route('/other_assets/delete/<asset_id>', methods=['POST'])
def delete_asset(asset_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    OtherAsset.delete_asset(asset_id)
    flash('Asset deleted successfully!', 'success')
    return redirect(url_for('other_assets.other_assets'))
