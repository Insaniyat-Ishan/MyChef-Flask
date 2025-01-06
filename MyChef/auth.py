import os
from flask import Blueprint, render_template, request, flash, redirect, url_for

from MyChef.views import UPLOAD_FOLDER
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.dashboard'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login_signup.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(
                email=email,
                first_name=first_name,
                password=generate_password_hash(password1, method='pbkdf2:sha256')  # Updated to pbkdf2:sha256
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.login'))

    return render_template("login_signup.html", user=current_user)


# Define the path for the uploaded files directly under static/uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'MyChef', 'static', 'uploads')  # Save uploads inside static/uploads
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@auth.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
       
        new_name = request.form.get('first_name')
        if new_name:
            current_user.first_name = new_name

        
        new_password = request.form.get('password')
        if new_password:
            current_user.password = generate_password_hash(new_password)

        
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture:
                filename = secure_filename(profile_picture.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)  # Save the image inside static/uploads
                profile_picture.save(filepath)
                current_user.profile_picture = filename  # Save the filename in the database

        
        allergies = request.form.getlist('allergies')  # Retrieve multiple checkbox values
        current_user.allergies = ', '.join(allergies)  # Save as a comma-separated string in the database

        
        diet_preference = request.form.get('diet_preference')
        if diet_preference:
            current_user.diet_preference = diet_preference

        
        health_issues = request.form.getlist('health_issues')  # Retrieve multiple checkbox values
        current_user.health_issues = ', '.join(health_issues)  # Save as a comma-separated string in the database

        
        db.session.commit()
        flash('Profile updated successfully!', category='success')
        return redirect(url_for('auth.edit_profile'))

   
    allergy_options = ['Peanuts', 'Dairy', 'Seafood', 'Gluten', 'Soy', 'Eggs']
    health_issue_options = ['Diabetes', 'High Blood Pressure', 'Heart Disease', 'Asthma', 'Allergies', 'Obesity']

    return render_template(
        'edit_profile.html',
        user=current_user,
        allergy_options=allergy_options,
        health_issue_options=health_issue_options
    )
