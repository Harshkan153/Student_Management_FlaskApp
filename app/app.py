from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__, template_folder="templates")
    bcrypt.init_app(app)
    app.config.from_object(Config)
    
    db.init_app(app)
   
    
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "students.login"

    
    from app.students.models import User
    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(uid)
    

    
    
    # students blueprint
    from app.students.routes import students
    app.register_blueprint(students, url_prefix='/students')
    
    #users blueprint
    from app.users.routes import users_bp
    app.register_blueprint(users_bp, url_prefix="/users")
    
    
    
    @app.route('/')
    def home():
        if current_user.is_authenticated:  # If the user is logged in, go to index
            return redirect(url_for('students.index'))
        return redirect(url_for('students.login'))  # Otherwise, redirect to login

    
    

    
    migrate = Migrate(app,db)
    
    return(app)