from . import db  # No need to worry about circular import now
from flask_login import UserMixin
from sqlalchemy.sql import func

from sqlalchemy.orm import relationship
from flask_login import UserMixin
from sqlalchemy.sql import func
from flask import current_app

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    profile_picture = db.Column(db.String(150), nullable=True, default="default.png")
    allergies = db.Column(db.String(150), nullable=True)  # Comma-separated string for multiple allergies
    diet_preference = db.Column(db.String(50), nullable=True)  # "Veg" or "Non-Veg"
    health_issues = db.Column(db.String(150), nullable=True)  # Comma-separated string for multiple health issues

    # Define the relationship to the MealPlan model using back_populates
    meal_plans = db.relationship('MealPlan', back_populates='user')


########## DB FOR RECIPE ##########
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cuisine = db.Column(db.String(100), nullable=True)
    image = db.Column(db.String(150), nullable=True)
    rating = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    
    # Relation
    ingredients = db.relationship('Ingredient', backref='recipe', cascade='all, delete-orphan')
    instructions = db.relationship('Instruction', backref='recipe', cascade='all, delete-orphan')
    meal_plans = db.relationship('MealPlan', back_populates='recipe')
    tags = db.relationship('Tag', secondary='recipe_tags', backref=db.backref('tags_in_recipe', lazy='dynamic'))


class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    ingredient = db.Column(db.String(150), nullable=False)


class Instruction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    instruction = db.Column(db.Text, nullable=False)
##############################################


class MealPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)  # Foreign key to Recipe

    # Explicit relationship names to avoid conflict
    user = db.relationship('User', back_populates='meal_plans')
    recipe = db.relationship('Recipe', back_populates='meal_plans')


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    # Relationship with Recipe (many-to-many via RecipeTags association table)
    recipes = db.relationship('Recipe', secondary='recipe_tags', backref=db.backref('recipes_in_tag', lazy='dynamic'))



class RecipeTags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)

