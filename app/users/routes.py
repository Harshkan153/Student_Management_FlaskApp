from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, jsonify

from flask_login import login_required, current_user

from app.app import db
from app.students.models import User


users_bp =Blueprint("users", __name__, template_folder="templates")


@users_bp.route("/users", methods=["GET"])
@login_required
def get_users():
    if not current_user.is_admin():
        return jsonify({"error": "Unauthorized access"}), 403

    users = User.query.all()
    return render_template("user_management.html", users=users)  # Ensure users is passed here



# Get a single user by ID (Admin Only)
@users_bp.route("/users/<int:user_id>", methods=["GET"])
@login_required
def get_user(user_id):
    if not current_user.is_admin():
        return jsonify({"error": "Unauthorized access"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_data = {"id": user.uid, "username": user.username, "email": user.email, "role": user.role}
    return jsonify(user_data), 200


# Update a user (Admin Only)
@users_bp.route("/update/<int:user_id>", methods=["PUT","GET"])
@login_required
def update_user(user_id):
    if not current_user.is_admin():
        return jsonify({"error": "Unauthorized access"}), 403
    user = User.query.get(user_id)
    if request.method == "GET":
        
        return render_template("edit_user.html",user=user)
    if not user:
        return jsonify({"error": "User not found"}), 404
    if request.method =="PUT":
        
        data = request.get_json()
        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)
        user.role = data.get("role", user.role)

        db.session.commit()
        return jsonify({"message": "User details updated successfully"}), 200


# Delete a user (Admin Only)
@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    if not current_user.is_admin():
        return jsonify({"error": "Unauthorized access"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200