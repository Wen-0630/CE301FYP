from datetime import datetime
from bson.objectid import ObjectId
from flask import current_app

class Notification:
    def __init__(self, user_id, message):
        self.user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        self.message = message
        self.created_at = datetime.utcnow()
        self.is_dismissed = False

    def save(self):
        notification = {
            'user_id': self.user_id,
            'message': self.message,
            'created_at': self.created_at,
            'is_dismissed': self.is_dismissed
        }
        result = current_app.mongo.db.notifications.insert_one(notification)
        return result.inserted_id

    @staticmethod
    def get_active_notifications(user_id):
        user_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
        notifications = list(current_app.mongo.db.notifications.find({
            'user_id': user_id,
            'is_dismissed': False
        }).sort('created_at', -1))
        return notifications


    @staticmethod
    def update_notification(notification_id):
        current_app.mongo.db.notifications.update_one(
            {'_id': ObjectId(notification_id)},
            {'$set': {'is_dismissed': True}}
        )


def send_saving_goal_notification(user_id, goal_name):
    # Check if a similar notification already exists
    existing_notification = current_app.mongo.db.notifications.find_one({
        'user_id': ObjectId(user_id),
        'message': f"Your saving goal '{goal_name}' has been achieved!",
        'is_dismissed': False
    })
    
    if not existing_notification:
        # If no such notification exists, create a new one
        message = f"Your saving goal '{goal_name}' has been achieved!"
        notification = Notification(user_id, message)
        notification.save()

def send_notification(user_id, message):
    # Check if a similar notification already exists
    existing_notification = current_app.mongo.db.notifications.find_one({
        'user_id': ObjectId(user_id),
        'message': message,
        'is_dismissed': False
    })
    
    if not existing_notification:
        # If no such notification exists, create a new one
        notification = Notification(user_id, message)
        notification.save()

def send_income_expense_ratio_notification(user_id, income_expense_ratio):
    """Sends a notification based on the income vs expense ratio."""
    if income_expense_ratio < 50:
        message = "Great job! Your income is significantly higher than your expenses."
    elif 90 <= income_expense_ratio <= 110:
        message = "You're breaking even. Consider reviewing your budget."
    elif income_expense_ratio > 120:
        message = "Alert: Your expenses are significantly higher than your income. It's time to take action!"
    else:
        # Default message if none of the above conditions are met
        message = "Keep monitoring your expenses and income to maintain financial stability."
    
    send_notification(user_id, message)

def send_budget_vs_spending_notification(user_id, radar_data):
    """Sends a notification based on budget vs actual spending data."""
    for i, indicator in enumerate(radar_data["indicators"]):
        budgeted_amount = radar_data["budget_values"][i]
        actual_spending = radar_data["actual_values"][i]
        category = indicator["text"]

        if actual_spending < 0.8 * budgeted_amount:
            message = f"Great job! Your spending on {category} is well below your budget."
        elif 0.8 <= actual_spending <= budgeted_amount:
            message = f"You're on track! Your spending on {category} is within your budget."
        elif actual_spending > budgeted_amount:
            message = f"Alert: Your spending on {category} has exceeded your budget!"

        send_notification(user_id, message)

