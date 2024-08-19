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

    is_automatic = 'automatic_saving_goal' in data  # Assuming checkbox is named 'automatic_saving_goal'

    if is_automatic:
        # Deactivate the current goal
        SavingGoal.deactivate_current_goal(user_id)

        # Create a new automatic goal
        target_amount = SavingGoal.calculate_automatic_target_amount(user_id)
        current_amount = SavingGoal.calculate_automatic_current_amount(user_id)
        target_date = SavingGoal.set_automatic_target_date()

        saving_goal = SavingGoal(
            user_id=user_id,
            name="Automatic Saving Goal",
            target_amount=target_amount,
            target_date=target_date,
            current_amount=current_amount,
            is_active=True,
            is_automatic=True
        )
        saving_goal.save()

    else:
        target_amount = float(data['target_amount'])
        target_date = datetime.datetime.strptime(data['target_date'], '%Y-%m-%d')

        # Deactivate the current goal
        SavingGoal.deactivate_current_goal(user_id)

        # Create a new user-set goal
        saving_goal = SavingGoal(
            user_id=user_id,
            name="My Saving Goal",
            target_amount=target_amount,
            target_date=target_date,
            current_amount=0,  # This will be calculated and updated
            is_active=True
        )
        saving_goal.save()

    return redirect(url_for('user.dashboard'))
