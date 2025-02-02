from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint

from flask_login import login_required, current_user

from app.app import db
from app.students.models import User


users_bp =Blueprint("users", __name__, template_folder="templates")


@users_bp.route("/")
@login_required
def manage_users():
    if not current_user.is_admin():
        flash("unauthorized access!", "danger")
        return redirect(url_for("students.index"))
    
    users = User.query.all()
    return render_template("user_management.html", users=users)



@users_bp.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        # Update user details
        user.username = request.form.get("username")
        user.email = request.form.get("email")
        user.role = request.form.get("role")  # You can also manage roles
        db.session.commit()
        flash("User details updated successfully!", "success")
        return redirect(url_for('users.manage_users'))
    
    return render_template("edit_user.html", user=user)


@users_bp.route("/delete/<int:u_id>", methods=["POST"])
@login_required
def delete_user(u_id):
    if not current_user.is_admin():
        flash("unauthorized access!", "danger")
        return redirect(url_for("users.manage_users"))
    
    user = User.query.get_or_404(u_id)
    db.session.delete(user)
    db.session.commit()
    flash("user deleted successfully")
    return redirect(url_for("users.manage_users"))
    
    