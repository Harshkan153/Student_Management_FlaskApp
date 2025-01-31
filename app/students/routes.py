from flask import abort, flash, jsonify, make_response, request, render_template, redirect, url_for, Blueprint

from io import BytesIO
import pandas as pd
from fpdf import FPDF
import plotly.graph_objects as go
import plotly.io as pio

from app.app import db
from app.students.models import Student, User


from flask_login import current_user, login_user, logout_user, login_required
from app.app import bcrypt


students = Blueprint("students", __name__, template_folder="templates", static_folder="static")





@students.route("/signup", methods = ["GET","POST"])
def signup():
    if request.method=="GET":
        return render_template("signup.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        role = request.form.get("role", "teacher")  # Default role is "teacher"
        
          # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists. Please use a different one or login.", "danger")
            return redirect(url_for("students.signup"))
            
        hashed_password = bcrypt.generate_password_hash(password)
            
        user = User(username=username, password=hashed_password,email=email,role=role)
            
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("students.login"))
    return render_template("signup.html")
    
    
    
@students.route("/login", methods=["GET","POST"])
def login():
        if request.method == "GET":
            return render_template("login.html")
        elif request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            
            user = User.query.filter(User.username == username).first()
            
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for("students.index"))
            else:
                flash("invalid Credentials", "Login failed")
                return redirect(url_for("students.login"))
        return render_template("login.html")
 
    
    
@students.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("students.login"))




@students.route("/index")
@login_required
def index():
    class_name = request.args.get("class")
    if class_name == "":  # Handle "All" option
        students = Student.query.all()  # Show all students
    elif class_name:  # Filter by class if a specific class is selected
        students = Student.query.filter_by(class_name=class_name).all()
    else:
        students = Student.query.all()
    return render_template("index.html", students = students, class_name=class_name)


@students.route("/view/<int:s_id>")
def view_student(s_id):
    student = Student.query.get_or_404(s_id)  # Retrieve student by ID, or return 404 if not found
    return render_template("view_student.html", student=student)



@students.route("/create", methods=["GET","POST"])
def create():
    if current_user.is_teacher() or current_user.is_admin():
        # Allow both admin and teacher to add a student
        if request.method == "GET":
            return render_template("add_student.html")
        elif request.method == "POST":
            name = request.form.get("name")
            age = int(request.form.get("age"))
            address = request.form.get("address")
            class_name = request.form.get("class_name")

            # Check for duplicate student
            existing_student = Student.query.filter_by(name=name, class_name=class_name).first()
            if existing_student:
                flash('Student already exists in this class.', 'error')
            else:
                new_student = Student(name=name, age=age, address=address, class_name=class_name)
                db.session.add(new_student)
                db.session.commit()
                flash('Student added successfully!', 'success')
            
            return redirect(url_for("students.index"))
    
    
    
@students.route("/update/<int:s_id>", methods=["GET","POST"])
@login_required
def update_student(s_id):
    if not current_user.is_admin():
        abort(403)  # Only Admin can edit students
    student = Student.query.get_or_404(s_id)
    if request.method == "POST":
        student.name = request.form["name"]
        student.age = request.form["age"]
        student.address = request.form["address"]
        student.class_name = request.form["class_name"]
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for("students.index"))
    return render_template("update_student.html", student=student)


@students.route("/delete/<int:s_id>")
@login_required
def delete_student(s_id):
    if not current_user.is_admin():
        abort(403) 
    student = Student.query.get_or_404(s_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully.', 'success')
    return redirect(url_for("students.index"))


@students.route("/export/json")
def export_json():
    all_students = Student.query.all()
    data = [{"name": s.name, "age": s.age, "address": s.address, "class_name": s.class_name} for s in all_students]
    return jsonify(data)

@students.route("/export/spreadsheet")
def export_spreadsheet():
    all_students = Student.query.all()
    data = [{"Name": s.name, "Age": s.age, "Address": s.address, "Class": s.class_name} for s in all_students]
    df = pd.DataFrame(data)

    # Create the Excel file using pandas
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Students")
    
    # Prepare response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=students.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return response



@students.route("/export/pdf")
def export_pdf():
    all_students = Student.query.all()

    # Create a PDF instance
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Set PDF title and font
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Student List", ln=True, align='C')

    # Add a line to separate the title from the table
    pdf.ln(10)

    # Set the header row for the table
    pdf.set_font("Arial", 'B', 12)

    # Column widths (adjust based on your data and requirement)
    column_widths = [60, 30, 60, 40]
    headers = ['Name', 'Age', 'Address', 'Class']

    # Add table headers with borders
    for i, header in enumerate(headers):
        pdf.cell(column_widths[i], 10, header, border=1, align='C')
    pdf.ln()

    # Set font for the table rows
    pdf.set_font("Arial", '', 12)

    # Add rows for each student
    for student in all_students:
        pdf.cell(column_widths[0], 10, student.name, border=1, align='C')
        pdf.cell(column_widths[1], 10, str(student.age), border=1, align='C')
        pdf.cell(column_widths[2], 10, student.address, border=1, align='C')
        pdf.cell(column_widths[3], 10, student.class_name, border=1, align='C')
        pdf.ln()

    # Generate the PDF response
    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers["Content-Disposition"] = "attachment; filename=students.pdf"
    response.headers["Content-Type"] = "application/pdf"
    return response

@students.route("/students_count")
def students_count():
    # Query the database to count students per class
    class_counts = db.session.query(
        Student.class_name, db.func.count(Student.s_id)
    ).group_by(Student.class_name).all()

    # Prepare data for the plot
    labels = [f"Class {c[0]}" for c in class_counts]
    values = [c[1] for c in class_counts]

    # Create a bar chart using Plotly
    fig = go.Figure(data=[
        go.Bar(
            x=labels, 
            y=values, 
            marker_color=['#FF5733', '#33FF57', '#3357FF', '#FF33A1'],  # Custom colors
            text=values,  # Show values on the bars
            textposition='auto',  # Position text automatically
            name="Students Per Class"  # Legend entry
        )
    ])
    
    fig.update_layout(
        title="Students Count per Class",  # Chart title
        title_font=dict(size=24, family='Arial', color='black'),  # Styled title
        title_x=0.5,
        xaxis=dict(
            title="Classes",  # X-axis label
            titlefont=dict(size=18),
            gridcolor='lightgrey',  # Gridlines color
        ),
        yaxis=dict(
            title="Number of Students",  # Y-axis label
            titlefont=dict(size=18),
            gridcolor='lightgrey',
            rangemode='tozero',  # Ensure the Y-axis starts at 0
           
        ),
        plot_bgcolor='rgba(245,245,245,1)',  # Background color
        paper_bgcolor='rgba(255,255,255,1)',  # Chart area color
        showlegend=True,  # Display the legend
        bargap=0.1,  # Reduce the gap between bars (default is 0.15, reducing it makes bars taller)
        height=600
    )

    # Generate HTML for the chart
    chart_html = pio.to_html(fig, full_html=False)

    return render_template("student_count.html", chart_html=chart_html)



