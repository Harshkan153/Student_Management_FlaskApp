from app.app import db

class Student(db.Model):
    __tablename__ = "students"
    s_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(10), nullable=False)
    
    
    def __repr__(self):
        return f"<student {self.name}>"