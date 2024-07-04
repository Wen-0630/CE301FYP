from flask import Blueprint, render_template, session, redirect, url_for, request, current_app
from bson.objectid import ObjectId
from src.transactions import calculate_total_transaction

cashflow_bp = Blueprint('cashflow_bp', __name__, template_folder='templates')

@cashflow_bp.route('/cashflow', methods=['GET', 'POST'])
def cashflow():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    cash_flow_collection = current_app.mongo.db.cash_flow

    if request.method == 'POST':
        initial_cash = float(request.form['initial_cash'])
        cash_flow_collection.update_one(
            {'userId': ObjectId(user_id)},
            {'$set': {'initial_cash': initial_cash}},
            upsert=True
        )
        return redirect(url_for('cashflow_bp.cashflow'))

    cash_flow_data = cash_flow_collection.find_one({'userId': ObjectId(user_id)})
    initial_cash = "{:.2f}".format(cash_flow_data['initial_cash']) if cash_flow_data else "{:.2f}".format(0.00)

    total_transaction = calculate_total_transaction(user_id)

    return render_template('cashflow.html', initial_cash=initial_cash, total_transaction="{:.2f}".format(total_transaction))
