from datetime import datetime
from flask import jsonify, render_template, request
from flask_login import  current_user
from app.app import db
from app.students.models import User

class ManageUsers:
    def __init__(self):
        self.response = {
            "job_status": True,
            "message": "",
            "issue_in_process": False,
            "errors": [],
        }

    
    def get(self, user_id=None):
        """Fetch all students or a single student"""
        try:
            if not current_user.is_admin():
                return jsonify({"error": "Unauthorized access"}), 403

            if user_id:
                user = User.query.get(user_id)
                if not user:
                    return jsonify({"job_status": False, "message": "User not found"}), 404

                user_data = {
                    "id": user.uid,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                }
                return jsonify(user_data), 200

            users = User.query.all()
            return render_template("user_management.html", users=users)

        except Exception as e:
            return jsonify({"job_status": False, "message": str(e)})

    
    def edit_user_form(self, user_id):
        """Render edit user form (GET request)"""
        try:
            if not current_user.is_admin():
                return jsonify({"error": "Unauthorized access"}), 403

            user = User.query.get(user_id)
            if not user:
                return jsonify({"job_status": False, "message": "User not found"}), 404

            return render_template("edit_user.html", user=user)

        except Exception as e:
            return jsonify({"job_status": False, "message": str(e)})

  

    def put(self, user_id):
        """Update student details (PUT request)"""
        try:
            if not current_user.is_admin():
                return jsonify({"error": "Unauthorized access"}), 403

            user = User.query.get(user_id)
            if not user:
                return jsonify({"job_status": False, "message": "User not found"}), 404

            data = request.get_json()
            user.username = data.get("username", user.username)
            user.email = data.get("email", user.email)
            user.role = data.get("role", user.role)

            db.session.commit()
            return jsonify({"job_status": True, "message": f"User {user.username} updated successfully"}), 200

        except Exception as e:
            return jsonify({"job_status": False, "message": str(e)})


    def delete(self, user_id):
        """Delete a student"""
        try:
            if not current_user.is_admin():
                return jsonify({"error": "Unauthorized access"}), 403

            user = User.query.get(user_id)
            if not user:
                return jsonify({"job_status": False, "message": "User not found"}), 404

            db.session.delete(user)
            db.session.commit()
            return jsonify({"job_status": True, "message": f"User {user.username} deleted successfully"}), 200

        except Exception as e:
            return jsonify({"job_status": False, "message": str(e)})
