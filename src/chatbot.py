from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, current_app
from dotenv import load_dotenv
import os
import json
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from bson.objectid import ObjectId
from .views import get_dashboard_data  
import re 

chatbot_bp = Blueprint('chatbot', __name__, template_folder='templates')

@chatbot_bp.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    if request.method == 'POST':
        user_query = request.json.get('user_query')

        # Fetch the user's dashboard data
        user_data = get_dashboard_data(user_id)

        # Get the chatbot's response
        chatbot_response = generate_chatbot_response(user_query, user_data)

        # Return the response as JSON
        return jsonify({'response': chatbot_response})

    # If GET request, render the chatbot page
    return render_template('chatbot.html')

def generate_chatbot_response(user_query, user_data):
    # Load environment variables and get your OpenAI API key
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise Exception("OPENAI_API_KEY not found in environment variables")

    # Check if the user is asking to update the initial cash amount
    update_cash_match = re.search(r'(?:update|change|set).*initial cash(?: amount)?(?:\s*to)?\s*\$?([\d,]+(?:\.\d{2})?)(?!\d)', user_query, re.IGNORECASE)
    if update_cash_match:
        # Remove commas, then convert to float
        new_cash_amount_str = update_cash_match.group(1).replace(",", "")
        new_cash_amount = float(new_cash_amount_str)
        update_initial_cash_amount(user_data['user']['_id'], new_cash_amount)
        return f"Your initial cash amount has been updated to ${new_cash_amount:,.2f}."

    # Format the user data into a context string
    context_lines = [
        f"Username: {user_data['user']['username']}",
        f"Email: {user_data['user']['email']}",
        f"Profile Picture: {user_data['user'].get('profile_pic', 'default_profile.png')}",
        f"Total Income: ${user_data['total_income']}",
        f"Total Expense: ${user_data['total_expense']}",
        f"Total Credit Card Outstanding: ${user_data['total_credit_card_outstanding']}",
        f"Total Loan Outstanding: ${user_data['total_loan_outstanding']}",
        f"Total Other Liabilities: ${user_data['total_other_liabilities']}",
        f"Total Outstanding Debt (Loans + Liabilities): ${user_data['total_outstanding']}",
        f"Positive amount of total investment is profit, negative amount is loss: ${user_data['total_investment']}. ",
        f"Net Cash Flow: ${user_data['net_cash_flow']}",
        f"Total Assets: ${user_data['total_assets']}",
        f"Net Worth: ${user_data['net_worth']}",
        f"Income-Expense Ratio: {user_data['income_expense_ratio']}%",
        f"Budget Message: {user_data['budget_message']}",
        f"Radar Chart Data: {user_data['radar_data_json']}",
        f"Saving Goals: " + ", ".join([f"{goal['name']}: Target ${goal['target_amount']}, Current ${goal['current_amount']}" for goal in user_data['saving_goals']]),
        f"Notifications: " + ", ".join([notif['message'] for notif in user_data['notifications']]),
        f"Top Asset Categories: " + ", ".join([f"{category['name']}: ${category['amount']}" for category in user_data['top_asset_categories']]),
        f"Top 5 Loans: " + ", ".join([f"{loan['name']}: Outstanding ${loan['outstanding_balance']}" for loan in user_data['top_5_loans']]),

    ]

    context = "\n".join(context_lines)

    # Define your prompt template
    template = """You are a helpful assistant.
When provided, use the following context to answer the user's question. If the context is relevant to the question, incorporate it into your answer. If the context is not relevant, or if it doesn't contain the information needed, answer the question based on your general knowledge.
{context}

Question: {question}

Helpful Answer:"""

    # Create the prompt
    prompt = PromptTemplate.from_template(template)
    prompt_text = prompt.format(context=context, question=user_query)

    # Initialize the language model
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=openai_api_key)

    # Get the response
    response = llm([HumanMessage(content=prompt_text)])

    return response.content

# Function to update initial cash amount in the database
def update_initial_cash_amount(user_id, new_cash_amount):
    cash_flow_collection = current_app.mongo.db.cash_flow
    cash_flow_collection.update_one(
        {'userId': ObjectId(user_id)},
        {'$set': {'initial_cash': new_cash_amount}},
        upsert=True
    )