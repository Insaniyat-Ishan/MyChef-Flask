# from flask import Blueprint, render_template
# from flask_login import login_required

# from flask_login import login_required, current_user

# from flask import Blueprint, render_template, request, flash, redirect, url_for
# from flask_login import login_required, current_user
# from werkzeug.utils import secure_filename
# from yourapp import db  # Assuming you have your db object imported
# from yourapp.models import Recipe, Ingredient, Instruction  # Assuming these models exist

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import Recipe, Ingredient, Instruction
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


@views.route('/dashboard')
@login_required  # This ensures that only logged-in users can access this page
def dashboard():
    return render_template('dashboard.html', user=current_user)



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