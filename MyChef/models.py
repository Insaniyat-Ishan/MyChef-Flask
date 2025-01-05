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
    allergies = db.Column(db.String(150), nullable=True)
    diet_preference = db.Column(db.String(50), nullable=True)
    health_issues = db.Column(db.String(150), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationship to MealPlan
    meal_plans = db.relationship('MealPlan', back_populates='user')

    # Relationship to Recipe
    recipes = db.relationship('Recipe', back_populates='user')

########## DB FOR RECIPE ##########
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cuisine = db.Column(db.String(100), nullable=True)
    image = db.Column(db.String(150), nullable=True)
    rating = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    reviews = db.relationship('Review', backref='reviews_in_recipe', cascade='all, delete-orphan')
    ingredients = db.relationship('Ingredient', backref='recipe', cascade='all, delete-orphan')
    instructions = db.relationship('Instruction', backref='recipe', cascade='all, delete-orphan')
    meal_plans = db.relationship('MealPlan', back_populates='recipe')
    tags = db.relationship('Tag', secondary='recipe_tags', backref=db.backref('tags_in_recipe', lazy='dynamic'))

    # Relationship to User
    user = db.relationship('User', back_populates='recipes')

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

###### REVIEW MODEL ######
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())

    # Relationships
    user = db.relationship('User', backref='reviews')
    recipe = db.relationship('Recipe', backref='reviews_in_recipe')  # Updated backref
###########################


##########favrecipe#########

class FavoriteRecipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    category = db.Column(db.String(100), nullable=True)  # Optional category field for organization
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    user = db.relationship('User', backref='favorites', lazy=True)
    recipe = db.relationship('Recipe', backref='favorited_by', lazy=True)
