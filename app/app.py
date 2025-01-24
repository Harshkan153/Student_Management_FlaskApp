from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)
    
    db.init_app(app)
    
    
    
    from app.students.routes import students
    app.register_blueprint(students, url_prefix='/students')
    
    
    
    # Adding a route for redirecting the root URL to /students/
    @app.route('/')
    def home():
        return redirect(url_for('students.index'))  # This redirects to the students' index route
    
    migrate = Migrate(app,db)
    
    return(app)