from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate  # Import Flask-Migrate


db = SQLAlchemy()
migrate = Migrate()  


DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ishannnnnnnnnnnnnn'  # Secret key for sessions
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  # SQLite database URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking to save resources

    # Initialize the database and migrate with the app
    db.init_app(app)
    migrate.init_app(app, db)  

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Redirect to login page if not logged in
    login_manager.init_app(app)

    from .models import User  # Import inside the function to avoid circular import
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    create_database(app)

    return app

def create_database(app):
    with app.app_context():  
        if not path.exists('website/' + DB_NAME): 
            db.create_all() 
            print('Created Database!')
