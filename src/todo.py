from flask import Blueprint, request, jsonify, session, current_app
from bson.objectid import ObjectId
from datetime import datetime

todo = Blueprint('todo', __name__)

@todo.route('/tasks', methods=['GET'])
def get_tasks():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    
    # Convert session user_id to ObjectId for MongoDB query
    tasks = list(current_app.mongo.db.todo_tasks.find({"user_id": ObjectId(user_id)}))
    for task in tasks:
        task['_id'] = str(task['_id'])  # Convert ObjectId to string for JSON compatibility
    return jsonify(tasks)

@todo.route('/tasks', methods=['POST'])
def add_task():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    
    data = request.get_json()
    task = {
        "user_id": ObjectId(user_id),  # Store user_id as ObjectId
        "task": data['task'],
        "completed": False,
        "created_at": datetime.now()
    }
    result = current_app.mongo.db.todo_tasks.insert_one(task)
    
    # Convert the ObjectId to a string for JSON compatibility
    task['_id'] = str(result.inserted_id)
    task['user_id'] = str(task['user_id'])  # Convert user_id as well, if needed
    
    return jsonify(task)  # Return the task with `_id` as a string


@todo.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    
    data = request.get_json()
    current_app.mongo.db.todo_tasks.update_one(
        {"_id": ObjectId(task_id), "user_id": ObjectId(user_id)},  # Match task with user_id
        {"$set": {"task": data['task'], "completed": data['completed']}}
    )
    return jsonify({"status": "success"})

@todo.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    
    current_app.mongo.db.todo_tasks.delete_one(
        {"_id": ObjectId(task_id), "user_id": ObjectId(user_id)}  # Match task with user_id
    )
    return jsonify({"status": "success"})
