from flask import Blueprint, request, jsonify, render_template, redirect, url_for, make_response
from flask.views import MethodView
from flask_login import login_user, logout_user, login_required, current_user
from io import BytesIO
import pandas as pd
from fpdf import FPDF
import plotly.graph_objects as go
from app.app import db, bcrypt
import plotly.io as pio

from app.students.models import Student, User

students = Blueprint("students", __name__, template_folder="templates", static_folder="static")

class SignupAPI(MethodView):
    def get(self):
        return render_template("signup.html")

    def post(self):
        data = request.json
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")
        role = data.get("role", "teacher")

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already exists"}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password, email=email, role=role)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Account created successfully"}), 201

class LoginAPI(MethodView):
    def get(self):
        return render_template("login.html")

    def post(self):
        data = request.json
        username = data.get("username")
        password = data.get("password")
        user = User.query.filter_by(username=username).first()

        if not user or not bcrypt.check_password_hash(user.password, password):
            return jsonify({"message": "Invalid username or password"}), 401

        login_user(user)
        return jsonify({"message": "Login successful", "user_id": user.uid, "role": user.role})

class LogoutAPI(MethodView):
    decorators = [login_required]

    def get(self):
        logout_user()
        return redirect(url_for("students.login"))

class StudentListAPI(MethodView):
    decorators = [login_required]

    def get(self):
        class_name = request.args.get("class")
        students = Student.query.filter_by(class_name=class_name).all() if class_name else Student.query.all()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify([{ "s_id": s.s_id, "name": s.name, "class_name": s.class_name, "age": s.age } for s in students])

        return render_template("index.html", students=students, is_admin=current_user.role == "admin")


class StudentAPI(MethodView):
    decorators = [login_required]

    def get(self):
        return render_template("add_student.html")

    def post(self):
        data = request.json
        student = Student(name=data["name"], age=int(data["age"]), address=data["address"], class_name=data["class_name"])
        db.session.add(student)
        db.session.commit()
        return jsonify({"message": "Student added successfully", "student_id": student.s_id})

class StudentUpdateAPI(MethodView):
    decorators = [login_required]

    def get(self, s_id):
        if not current_user.is_admin():
            return jsonify({"message": "Permission denied"}), 403
        student = Student.query.get(s_id)
        if not student:
            return jsonify({"message": "Student not found"}), 404
        return render_template("update_student.html", student=student)
    
    def post(self, s_id):
        if not current_user.is_admin():
            return jsonify({"message": "Permission denied"}), 403

        student = Student.query.get_or_404(s_id)
        data = request.json
        student.name = data.get("name", student.name)
        student.age = data.get("age", student.age)
        student.address = data.get("address", student.address)
        student.class_name = data.get("class_name", student.class_name)
        db.session.commit()
        return jsonify({"message": "Student updated successfully"})

class StudentDeleteAPI(MethodView):
    decorators = [login_required]

    def delete(self, s_id):
        if not current_user.is_admin():
            return jsonify({"message": "Permission denied"}), 403

        student = Student.query.get(s_id)
        if not student:
            return jsonify({"message": "Student not found"}), 404

        db.session.delete(student)
        db.session.commit()
        return jsonify({"message": "Student deleted successfully"})
    
    
    
class ExportJSONAPI(MethodView):
    def get(self):
        all_students = Student.query.all()
        data = [{"name": s.name, "age": s.age, "address": s.address, "class_name": s.class_name} for s in all_students]
        return jsonify(data)

class ExportSpreadsheetAPI(MethodView):
    def get(self):
        all_students = Student.query.all()
        data = [{"Name": s.name, "Age": s.age, "Address": s.address, "Class": s.class_name} for s in all_students]
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Students")
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=students.xlsx"
        response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        return response

class ExportPDFAPI(MethodView):
    def get(self):
        all_students = Student.query.all()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Student List", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        for student in all_students:
            pdf.cell(60, 10, student.name, border=1)
            pdf.cell(30, 10, str(student.age), border=1)
            pdf.cell(60, 10, student.address, border=1)
            pdf.cell(40, 10, student.class_name, border=1)
            pdf.ln()
        response = make_response(pdf.output(dest='S').encode('latin1'))
        response.headers["Content-Disposition"] = "attachment; filename=students.pdf"
        response.headers["Content-Type"] = "application/pdf"
        return response
    
    
class StudentsCountAPI(MethodView):
    def get(self):
        class_counts = db.session.query(
            Student.class_name, db.func.count(Student.s_id)
        ).group_by(Student.class_name).all()

        labels = [f"Class {c[0]}" for c in class_counts]
        values = [c[1] for c in class_counts]

        fig = go.Figure(data=[
            go.Bar(
                x=labels, 
                y=values, 
                marker_color=['#FF5733', '#33FF57', '#3357FF', '#FF33A1'],
                text=values,  
                textposition='auto',
                name="Students Per Class"
            )
        ])
        
        fig.update_layout(
            title="Students Count per Class",  
            title_font=dict(size=24, family='Arial', color='black'),  
            title_x=0.5,
            xaxis=dict(
                title="Classes",  
                titlefont=dict(size=18),
                gridcolor='lightgrey',  
            ),
            yaxis=dict(
                title="Number of Students",  
                titlefont=dict(size=18),
                gridcolor='lightgrey',
                rangemode='tozero',  
            ),
            plot_bgcolor='rgba(245,245,245,1)',  
            paper_bgcolor='rgba(255,255,255,1)',  
            showlegend=True,  
            bargap=0.1,  
            height=600
        )

        chart_html = pio.to_html(fig, full_html=False)
        return render_template("student_count.html", chart_html=chart_html)



students.add_url_rule("/signup", view_func=SignupAPI.as_view("signup"))
students.add_url_rule("/login", view_func=LoginAPI.as_view("login"))
students.add_url_rule("/logout", view_func=LogoutAPI.as_view("logout"))
students.add_url_rule("/students", view_func=StudentListAPI.as_view("students"))
students.add_url_rule("/create", view_func=StudentAPI.as_view("create"))
students.add_url_rule("/update/<int:s_id>", view_func=StudentUpdateAPI.as_view("update_student"))
students.add_url_rule("/students/<int:s_id>", view_func=StudentDeleteAPI.as_view("delete_student"), methods=["DELETE"])
students.add_url_rule("/", view_func=StudentListAPI.as_view("index"))
students.add_url_rule("/export/json", view_func=ExportJSONAPI.as_view("export_json"))
students.add_url_rule("/export/spreadsheet", view_func=ExportSpreadsheetAPI.as_view("export_spreadsheet"))
students.add_url_rule("/export/pdf", view_func=ExportPDFAPI.as_view("export_pdf"))
students.add_url_rule("/students_count", view_func=StudentsCountAPI.as_view("students_count"))