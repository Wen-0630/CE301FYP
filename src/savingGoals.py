from flask import Blueprint, request, session, redirect, url_for
from .models import SavingGoal
import datetime

savingGoals_bp = Blueprint('saving_goals', __name__)

@savingGoals_bp.route('/saving_goals/edit', methods=['POST'])
def edit_saving_goal():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    data = request.form.to_dict()
    target_amount = float(data['target_amount'])
    target_date = datetime.datetime.strptime(data['target_date'], '%Y-%m-%d')

    # Deactivate the current goal
    SavingGoal.deactivate_current_goal(user_id)

    # Create a new goal with the updated values
    saving_goal = SavingGoal(
        user_id=user_id,
        name="My Saving Goal",  # Default name, or allow user to set this
        target_amount=target_amount,
        target_date=target_date,
        current_amount=0,  # This will be calculated and updated
        is_active=True
    )
    goal_id = saving_goal.save()

    # Recalculate the current amount for the new goal
    SavingGoal.calculate_current_amount(goal_id, user_id)

    return redirect(url_for('user.dashboard'))
