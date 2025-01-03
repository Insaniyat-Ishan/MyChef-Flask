from flask import Blueprint, render_template
from flask_login import login_required

from flask_login import login_required, current_user



views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('index.html')

@views.route('/login', methods=['GET'])
def login():
    return render_template('login_signup.html')


@views.route('/dashboard')
@login_required  # This ensures that only logged-in users can access this page
def dashboard():
    return render_template('dashboard.html', user=current_user)

@views.route('/recipe_details')
def recipe_details():
    return render_template('recipe_details.html')