from app.app import db
from flask_login import UserMixin



class Student(db.Model):
    __tablename__ = "students"
    s_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(10), nullable=False)
    
    
    def __repr__(self):
        return f"<student {self.name}>"
    
    
class User(db.Model,UserMixin):
    __tablename__ = "users"
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120),nullable=False)
    role = db.Column(db.String(20), nullable=False, default="teacher") 
    
       
    
    def get_id(self):
        return str(self.uid)
    
    def is_admin(self):
        return self.role == "admin"

    def is_teacher(self):
        return self.role == "teacher"