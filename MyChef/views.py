# from flask import Blueprint, render_template
# from flask_login import login_required

# from flask_login import login_required, current_user

# from flask import Blueprint, render_template, request, flash, redirect, url_for
# from flask_login import login_required, current_user
# from werkzeug.utils import secure_filename
# from yourapp import db  # Assuming you have your db object imported
# from yourapp.models import Recipe, Ingredient, Instruction  # Assuming these models exist
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import MealPlan
from datetime import datetime, timedelta
import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import MealPlan, Recipe, Ingredient, Instruction
from werkzeug.utils import secure_filename

views = Blueprint('views', __name__)

@views.route('/')
def home():
    if current_user.is_authenticated:
        # If the user is logged in, redirect to the dashboard
        return redirect(url_for('views.dashboard'))
    # If the user is not logged in, render the index page
    return render_template('index.html')


@views.route('/login', methods=['GET'])
def login():
    return render_template('login_signup.html')


from datetime import datetime, timedelta, date  # Ensure you import timedelta here


@views.route('/dashboard')
@login_required
def user_dashboard():
    # Get the current date and calculate the start of the week (Monday)
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    
    # Query the meal plans for the current user
    meal_plans = MealPlan.query.filter_by(user_id=current_user.id).all()

    # Prepare a list of meals for each day of the week
    weekly_meals = [
        {
            'day': start_of_week + timedelta(days=day),
            'meals': [meal for meal in meal_plans if meal.date == (start_of_week + timedelta(days=day)).date()]
        }
        for day in range(7)
    ]

    # Render the dashboard template and pass the weekly meals
    return render_template('dashboard.html', weekly_meals=weekly_meals, start_of_week=start_of_week)



#Recipe adding 
import os

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'MyChef', 'static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@views.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'GET':
        return render_template('add_recipe.html', user=current_user)
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        cuisine = request.form.get('cuisine')
        image = request.files.get('image')  # Get the uploaded file

        # Validate input
        if not name or not cuisine:
            flash('Name and Cuisine are required!', category='error')
            return render_template('add_recipe.html', user=current_user)

        # Handle image saving
        if image:
            print("I AM HERE")
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)  # Use the full path
            image.save(image_path)  # Save image in the uploads folder
            relative_image_path = f'uploads/{filename}'
        else:
            relative_image_path = None

        # Create a new Recipe instance
        new_recipe = Recipe(
            name=name,
            description=description,
            cuisine=cuisine,
            image=relative_image_path,  # Save relative path to the database
            rating=0  # Initialize with 0 rating
        )
        db.session.add(new_recipe)
        db.session.commit()

        # Add ingredients
        ingredients = request.form.get('ingredients')  # Make sure you collect all ingredients as a comma-separated string
        for ingredient in ingredients.split(','):
            new_ingredient = Ingredient(
                recipe_id=new_recipe.id,
                ingredient=ingredient.strip()
            )
            db.session.add(new_ingredient)

        # Add instructions
        instructions = request.form.get('instructions')  # Make sure you collect all instructions
        for step_number, instruction in enumerate(instructions.split('\n'), start=1):
            new_instruction = Instruction(
                recipe_id=new_recipe.id,
                step_number=step_number,
                instruction=instruction.strip()
            )
            db.session.add(new_instruction)

        # Commit everything to the database
        db.session.commit()

        flash('Recipe added successfully!', category='success')
        return redirect(url_for('views.dashboard'))

    return render_template('add_recipe.html', user=current_user)


######## ALL RECIPES ##############
from . import db
from .models import Recipe

@views.route('/recipes', methods=['GET'])
def recipes():
    # Fetch all recipes from the database
    all_recipes = Recipe.query.all()
    return render_template('recipes.html', recipes=all_recipes)


######### RECIPE DETAILS ################
@views.route('/recipe/<int:recipe_id>', methods=['GET'])
def recipe_details(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe:
        print("something")
        return render_template('recipe_details.html', recipe=recipe)
    return "ERROR"

######## Handle Chatbot ################
def generate_response(user_message):
    if "hello" in user_message.lower():
        return "Hi there! How can I help you today?"
    elif "recipe" in user_message.lower():
        return "I can help you with recipes. What type of cuisine are you interested in?"
    else:
        return "I'm not sure I understand. Can you please rephrase?"

@views.route('/chatbot', methods=['GET'])
def chatbot():
    return render_template('chatbot.html')

@views.route('/temp', methods=['GET'])
def temp():
    return render_template('temp.html')

from flask import jsonify

@views.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    response = generate_response(user_message)
    return jsonify({'response': response})


@views.route('/dashboard')
@login_required
def dashboard():
    # Fetch the meal plan data for the logged-in user for the current week
    meal_plans = MealPlan.query.filter_by(user_id=current_user.id).all()
    
    # Get the current date and calculate the week range
    today = datetime.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())  # Monday of the current week
    end_of_week = start_of_week + datetime.timedelta(days=6)  # Sunday of the current week
    
    # Filter the meal plans to show only those within this week
    weekly_meals = [meal for meal in meal_plans if start_of_week <= meal.date <= end_of_week]

    # Pass meal plan data to the template
    return render_template('dashboard.html', meals=weekly_meals, start_of_week=start_of_week)


from flask import  request

# views.py
from flask import render_template, request, redirect, url_for
from .models import MealPlan, Recipe
from flask_login import login_required, current_user

@views.route('/add_meal', methods=['GET', 'POST'])
@login_required
def add_meal():
    if request.method == 'POST':
        # Get the form data
        name = request.form['name']
        date_string = request.form['date']  # Date format 'YYYY-MM-DD'
        recipe_id = request.form['recipe_id']
        
        # Convert the date string to a datetime.date object
        date_object = datetime.strptime(date_string, '%Y-%m-%d').date()

        # Create a new meal plan entry
        meal_plan = MealPlan(
            name=name,
            date=date_object,
            user_id=current_user.id,  # Use the logged-in user's ID
            recipe_id=recipe_id
        )

        # Add and commit to the database
        db.session.add(meal_plan)
        db.session.commit()

        flash('Meal added successfully!', category='success')
        return redirect(url_for('views.user_dashboard'))  # Redirect to user dashboard

    # Fetch all recipes to display in the dropdown
    recipes = Recipe.query.all()
    return render_template('add_meal.html', recipes=recipes)



# Route for removing a meal
@views.route('/remove_meal/<int:meal_id>/<date>', methods=['POST'])
def remove_meal(meal_id, date):
    meal = MealPlan.query.get(meal_id)  # Changed Meal to MealPlan
    if meal:
        db.session.delete(meal)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

# Route for replacing a meal
@views.route('/replace_meal/<int:meal_id>/<date>', methods=['POST'])
def replace_meal(meal_id, date):
    data = request.get_json()
    new_recipe_name = data.get('newRecipeName')

    # Find the new recipe (this can be adjusted to your logic for replacing)
    new_recipe = Recipe.query.filter_by(name=new_recipe_name).first()

    if new_recipe:
        meal = MealPlan.query.get(meal_id)  # Changed Meal to MealPlan
        if meal:
            meal.recipe = new_recipe
            db.session.commit()
            return jsonify({'success': True})
    return jsonify({'success': False})


