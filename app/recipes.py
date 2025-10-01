from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange
from app.models import db, Recipe, InventoryItem
import json
import google.generativeai as genai
from config import Config

recipes_bp = Blueprint('recipes', __name__)

class RecipeForm(FlaskForm):
    name = StringField('Recipe Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    ingredients = TextAreaField('Ingredients (one per line, format: quantity unit item)')
    instructions = TextAreaField('Cooking Instructions')
    prep_time = IntegerField('Prep Time (minutes)', validators=[NumberRange(min=0)])
    cook_time = IntegerField('Cook Time (minutes)', validators=[NumberRange(min=0)])
    servings = IntegerField('Servings', validators=[DataRequired(), NumberRange(min=1)], default=1)
    category = SelectField('Category', choices=[
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
        ('dessert', 'Dessert'),
        ('beverage', 'Beverage')
    ])
    difficulty = SelectField('Difficulty', choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ])
    tags = TextAreaField('Tags (one per line)')
    submit = SubmitField('Save Recipe')

@recipes_bp.route('/')
@login_required
def index():
    """Display all recipes"""
    recipes = Recipe.query.filter_by(user_id=current_user.id).order_by(Recipe.created_at.desc()).all()
    return render_template('recipes/index.html', recipes=recipes)

@recipes_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new recipe"""
    form = RecipeForm()
    
    if form.validate_on_submit():
        # Parse ingredients
        ingredients_list = []
        for line in form.ingredients.data.split('\n'):
            line = line.strip()
            if line:
                ingredients_list.append(line)
        
        # Parse tags
        tags_list = []
        for line in form.tags.data.split('\n'):
            line = line.strip()
            if line:
                tags_list.append(line)
        
        recipe = Recipe(
            user_id=current_user.id,
            name=form.name.data,
            description=form.description.data,
            instructions=form.instructions.data,
            prep_time=form.prep_time.data,
            cook_time=form.cook_time.data,
            servings=form.servings.data,
            category=form.category.data,
            difficulty=form.difficulty.data
        )
        recipe.set_ingredients(ingredients_list)
        recipe.set_tags(tags_list)
        
        db.session.add(recipe)
        db.session.commit()
        
        flash('Recipe created successfully!', 'success')
        return redirect(url_for('recipes.view', id=recipe.id))
    
    return render_template('recipes/create.html', form=form)

@recipes_bp.route('/<int:id>')
@login_required
def view(id):
    """View a specific recipe"""
    recipe = Recipe.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('recipes/view.html', recipe=recipe)

@recipes_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit a recipe"""
    recipe = Recipe.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = RecipeForm()
    
    if request.method == 'GET':
        # Populate form with current recipe data
        form.name.data = recipe.name
        form.description.data = recipe.description
        form.ingredients.data = '\n'.join(recipe.get_ingredients())
        form.instructions.data = recipe.instructions
        form.prep_time.data = recipe.prep_time
        form.cook_time.data = recipe.cook_time
        form.servings.data = recipe.servings
        form.category.data = recipe.category
        form.difficulty.data = recipe.difficulty
        form.tags.data = '\n'.join(recipe.get_tags())
    
    if form.validate_on_submit():
        # Parse ingredients
        ingredients_list = []
        for line in form.ingredients.data.split('\n'):
            line = line.strip()
            if line:
                ingredients_list.append(line)
        
        # Parse tags
        tags_list = []
        for line in form.tags.data.split('\n'):
            line = line.strip()
            if line:
                tags_list.append(line)
        
        # Update recipe
        recipe.name = form.name.data
        recipe.description = form.description.data
        recipe.set_ingredients(ingredients_list)
        recipe.instructions = form.instructions.data
        recipe.prep_time = form.prep_time.data
        recipe.cook_time = form.cook_time.data
        recipe.servings = form.servings.data
        recipe.category = form.category.data
        recipe.difficulty = form.difficulty.data
        recipe.set_tags(tags_list)
        
        db.session.commit()
        flash('Recipe updated successfully!', 'success')
        return redirect(url_for('recipes.view', id=recipe.id))
    
    return render_template('recipes/edit.html', form=form, recipe=recipe)

@recipes_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a recipe"""
    recipe = Recipe.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(recipe)
    db.session.commit()
    flash('Recipe deleted successfully!', 'success')
    return redirect(url_for('recipes.index'))

@recipes_bp.route('/suggest', methods=['POST'])
@login_required
def suggest_recipe():
    """Generate recipe suggestions using AI based on available ingredients"""
    try:
        if not Config.GEMINI_API_KEY:
            return jsonify({'error': 'AI integration not configured'}), 400
        
        # Configure Gemini
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        # Get user's inventory
        inventory_items = InventoryItem.query.filter_by(user_id=current_user.id).all()
        available_ingredients = [f"{item.name} ({item.quantity} {item.unit})" for item in inventory_items if item.quantity > 0]
        
        if not available_ingredients:
            return jsonify({'error': 'No ingredients available in inventory'}), 400
        
        # Get user preferences
        dietary_restrictions = current_user.get_dietary_restrictions()
        taste_preferences = current_user.get_taste_preferences()
        family_size = current_user.family_size
        
        # Create prompt
        prompt = f"""
        Suggest 3 recipes that can be made with the following available ingredients:
        
        Available ingredients: {', '.join(available_ingredients)}
        Family size: {family_size} people
        Dietary restrictions: {', '.join(dietary_restrictions) if dietary_restrictions else 'None'}
        Taste preferences: {', '.join(taste_preferences) if taste_preferences else 'None'}
        
        For each recipe, provide:
        1. Recipe name
        2. Brief description
        3. Ingredients needed (with quantities)
        4. Step-by-step cooking instructions
        5. Prep time and cook time
        6. Difficulty level (easy/medium/hard)
        7. Category (breakfast/lunch/dinner/snack/dessert/beverage)
        
        Format the response as JSON with this structure:
        {{
            "recipes": [
                {{
                    "name": "Recipe Name",
                    "description": "Brief description",
                    "ingredients": ["quantity unit ingredient"],
                    "instructions": ["step 1", "step 2", ...],
                    "prep_time": 15,
                    "cook_time": 30,
                    "difficulty": "easy",
                    "category": "dinner",
                    "servings": {family_size}
                }}
            ]
        }}
        """
        
        response = model.generate_content(prompt)
        recipe_data = json.loads(response.text)
        
        return jsonify(recipe_data)
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate recipe suggestions: {str(e)}'}), 500

@recipes_bp.route('/suggest/save', methods=['POST'])
@login_required
def save_suggested_recipe():
    """Save a suggested recipe to user's collection"""
    try:
        data = request.json
        recipe_data = data.get('recipe')
        
        if not recipe_data:
            return jsonify({'error': 'No recipe data provided'}), 400
        
        recipe = Recipe(
            user_id=current_user.id,
            name=recipe_data['name'],
            description=recipe_data.get('description', ''),
            instructions='\n'.join(recipe_data.get('instructions', [])),
            prep_time=recipe_data.get('prep_time', 0),
            cook_time=recipe_data.get('cook_time', 0),
            servings=recipe_data.get('servings', current_user.family_size),
            category=recipe_data.get('category', 'dinner'),
            difficulty=recipe_data.get('difficulty', 'easy'),
            is_ai_generated=True
        )
        recipe.set_ingredients(recipe_data.get('ingredients', []))
        
        db.session.add(recipe)
        db.session.commit()
        
        return jsonify({'success': True, 'recipe_id': recipe.id})
        
    except Exception as e:
        return jsonify({'error': f'Failed to save recipe: {str(e)}'}), 500

@recipes_bp.route('/cook/<int:id>', methods=['POST'])
@login_required
def cook_recipe(id):
    """Mark a recipe as cooked and update inventory"""
    recipe = Recipe.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        # Parse ingredients and update inventory
        ingredients = recipe.get_ingredients()
        for ingredient_line in ingredients:
            # Simple parsing - assumes format like "1 cup rice" or "2 tbsp oil"
            parts = ingredient_line.strip().split()
            if len(parts) >= 3:
                try:
                    quantity = float(parts[0])
                    unit = parts[1]
                    item_name = ' '.join(parts[2:])
                    
                    # Find matching inventory item
                    inventory_item = InventoryItem.query.filter_by(
                        user_id=current_user.id,
                        name=item_name
                    ).first()
                    
                    if inventory_item:
                        # Reduce quantity
                        new_quantity = max(0, inventory_item.quantity - quantity)
                        inventory_item.quantity = new_quantity
                        
                except ValueError:
                    # Skip if quantity can't be parsed
                    continue
        
        db.session.commit()
        flash(f'Recipe "{recipe.name}" marked as cooked! Inventory updated.', 'success')
        
    except Exception as e:
        flash(f'Error updating inventory: {str(e)}', 'error')
    
    return redirect(url_for('recipes.view', id=recipe.id))

