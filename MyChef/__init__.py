from flask import Flask
from .views import views  # Import your views blueprint

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    # Register the views blueprint
    app.register_blueprint(views, url_prefix='/')

    return app
