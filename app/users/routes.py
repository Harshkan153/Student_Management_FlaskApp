from flask import Blueprint
from flask_login import login_required
from app.users.Manage_Users import ManageUsers  # Import the new class

users_bp = Blueprint("users", __name__, template_folder="templates")
users_service = ManageUsers()

@users_bp.route("/users", methods=["GET"])
@login_required
def get_users():
    return users_service.get()

@users_bp.route("/users/<int:user_id>", methods=["GET"])
@login_required
def get_user(user_id):
    return users_service.get(user_id)

@users_bp.route("/users", methods=["POST"])
@login_required
def add_user():
    return users_service.post()

@users_bp.route("/users/update/<int:user_id>", methods=["PUT"])
@login_required
def update_user(user_id):
    return users_service.put(user_id)

@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    return users_service.delete(user_id)

@users_bp.route("/users/update/<int:user_id>", methods=["GET"])
@login_required
def edit_user(user_id):
    return users_service.edit_user_form(user_id)

