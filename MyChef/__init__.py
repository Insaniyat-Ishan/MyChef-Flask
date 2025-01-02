from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# Initialize the database
db = SQLAlchemy()
# Define the database name
DB_NAME = "database.db"

# Initialize the Flask app and configure it
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ishannnnnnnnnnnnnn'  # Secret key for sessions
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  # SQLite database URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking to save resources

    # Initialize the database with the app
    db.init_app(app)

    # Register the blueprints
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Initialize the login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Redirect to login page if not logged in
    login_manager.init_app(app)

    # Define the user loader for the login manager
    from .models import User  # Import inside the function to avoid circular import
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Create the database if it doesn't exist
    create_database(app)

    return app

# Function to create the database if it doesn't exist
def create_database(app):
    with app.app_context():  # Use app context to create the database
        if not path.exists('website/' + DB_NAME):  # Check if the database file exists
            db.create_all()  # Create all tables from models
            print('Created Database!')
