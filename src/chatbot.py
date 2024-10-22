from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, current_app
from dotenv import load_dotenv
import os
import json
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from bson.objectid import ObjectId
import datetime

# Import necessary modules and functions
from .models import Transaction, Loan, SavingGoal
from .transactions import calculate_total_income, calculate_total_expense
from .creditCard import get_total_outstanding
from .investment import calculate_total_investment_profit_loss
from .cashFlow import get_net_cash_flow
from .budget import BudgetManager
from .notifications import Notification

# Create a Blueprint for chatbot-related routes
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

def get_dashboard_data(user_id):
    # Fetch user data as you do in the dashboard route
    user = current_app.mongo.cx['CE-301'].users.find_one({"_id": ObjectId(user_id)})
    if 'profile_pic' not in user:
        user['profile_pic'] = 'default_profile.png'

    total_income = calculate_total_income(user_id)
    total_expense = calculate_total_expense(user_id)
    total_credit_card_outstanding = get_total_outstanding(user_id)

    loans = Loan.get_all_loans_by_user(ObjectId(user_id))
    total_loan_outstanding = sum(loan['outstanding_balance'] + loan['interest_balance'] for loan in loans)
    total_outstanding = total_credit_card_outstanding + total_loan_outstanding

    total_investment = calculate_total_investment_profit_loss(user_id)
    net_cash_flow = get_net_cash_flow(user_id)
    net_worth = net_cash_flow + total_investment - total_outstanding

    saving_goals = SavingGoal.get_goals_by_user(user_id)
    for goal in saving_goals:
        # Update the current amount before rendering the dashboard
        SavingGoal.calculate_current_amount(goal['_id'], user_id)

    if total_expense > 0 and total_income > 0:
        income_expense_ratio = round((total_expense / total_income) * 100, 2)
    elif total_income > 0:
        income_expense_ratio = 0.00  # Set the ratio to 0 if income exists but expense is nil
    else:
        income_expense_ratio = 100.00

    budget = BudgetManager.get_latest_budget(user_id)
    if budget:
        radar_data = BudgetManager.prepare_radar_chart_data(
            user_id,
            budget['categories'],
            budget['budget_amounts'],
            budget['start_date'],
            budget['end_date']
        )
        budget_message = ""
    else:
        radar_data = {}
        budget_message = "No active budget. Please set a budget."

    notifications = Notification.get_active_notifications(user_id)

    # Prepare data for the chatbot
    data = {
        "user": {
            "username": user['username'],
            "email": user['email'],
            "profile_pic": user['profile_pic']
        },
        "total_income": total_income,
        "total_expense": total_expense,
        "total_outstanding": total_outstanding,
        "total_investment": total_investment,
        "net_cash_flow": net_cash_flow,
        "net_worth": net_worth,
        "income_expense_ratio": income_expense_ratio,
        "budget_message": budget_message,
        # Add other data as needed
    }

    return data

def generate_chatbot_response(user_query, user_data):
    # Load environment variables and get your OpenAI API key
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise Exception("OPENAI_API_KEY not found in environment variables")

    # Format the user data into a context string
    context_lines = []
    context_lines.append(f"User: {user_data['user']['username']}")
    context_lines.append(f"Total Income: {user_data['total_income']}")
    context_lines.append(f"Total Expense: {user_data['total_expense']}")
    context_lines.append(f"Net Cash Flow: {user_data['net_cash_flow']}")
    context_lines.append(f"Total Assets: {user_data['net_cash_flow']}")
    context_lines.append(f"Net Worth: {user_data['net_worth']}")
    context_lines.append(f"Income-Expense Ratio: {user_data['income_expense_ratio']}%")
    context_lines.append(f"Total Investment: {user_data['total_investment']}")
    context_lines.append(f"Total Outstanding: {user_data['total_outstanding']}")
    # Add more fields as needed

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
