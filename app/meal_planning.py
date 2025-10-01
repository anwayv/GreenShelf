from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, IntegerField, SubmitField, StringField
from wtforms.validators import DataRequired, NumberRange
from app.models import db, MealPlan, Recipe, InventoryItem
from datetime import datetime, date, timedelta
import json

meal_planning_bp = Blueprint('meal_planning', __name__)

class MealPlanForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    meal_type = SelectField('Meal Type', choices=[
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack')
    ], validators=[DataRequired()])
    recipe_id = SelectField('Recipe', coerce=int)
    custom_meal_name = StringField('Custom Meal Name')
    servings = IntegerField('Servings', validators=[DataRequired(), NumberRange(min=1)], default=1)
    submit = SubmitField('Add to Meal Plan')

@meal_planning_bp.route('/')
@login_required
def index():
    """Display meal planning calendar"""
    # Get current week
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    
    # Get meal plans for the week
    meal_plans = {}
    for week_date in week_dates:
        plans = MealPlan.query.filter_by(
            user_id=current_user.id,
            date=week_date
        ).order_by(MealPlan.meal_type).all()
        meal_plans[week_date] = plans
    
    return render_template('meal_planning/index.html', 
                         week_dates=week_dates, 
                         meal_plans=meal_plans,
                         today=today)

@meal_planning_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a meal to the meal plan"""
    form = MealPlanForm()
    
    # Populate recipe choices
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    form.recipe_id.choices = [(0, 'Custom Meal')] + [(r.id, r.name) for r in recipes]
    
    if form.validate_on_submit():
        meal_plan = MealPlan(
            user_id=current_user.id,
            date=form.date.data,
            meal_type=form.meal_type.data,
            servings=form.servings.data
        )
        
        if form.recipe_id.data and form.recipe_id.data != 0:
            meal_plan.recipe_id = form.recipe_id.data
        else:
            meal_plan.custom_meal_name = form.custom_meal_name.data
        
        db.session.add(meal_plan)
        db.session.commit()
        
        flash('Meal added to plan successfully!', 'success')
        return redirect(url_for('meal_planning.index'))
    
    return render_template('meal_planning/add.html', form=form)

@meal_planning_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit a meal plan entry"""
    meal_plan = MealPlan.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = MealPlanForm()
    
    # Populate recipe choices
    recipes = Recipe.query.filter_by(user_id=current_user.id).all()
    form.recipe_id.choices = [(0, 'Custom Meal')] + [(r.id, r.name) for r in recipes]
    
    if request.method == 'GET':
        form.date.data = meal_plan.date
        form.meal_type.data = meal_plan.meal_type
        form.recipe_id.data = meal_plan.recipe_id or 0
        form.custom_meal_name.data = meal_plan.custom_meal_name
        form.servings.data = meal_plan.servings
    
    if form.validate_on_submit():
        meal_plan.date = form.date.data
        meal_plan.meal_type = form.meal_type.data
        meal_plan.servings = form.servings.data
        
        if form.recipe_id.data and form.recipe_id.data != 0:
            meal_plan.recipe_id = form.recipe_id.data
            meal_plan.custom_meal_name = None
        else:
            meal_plan.recipe_id = None
            meal_plan.custom_meal_name = form.custom_meal_name.data
        
        db.session.commit()
        flash('Meal plan updated successfully!', 'success')
        return redirect(url_for('meal_planning.index'))
    
    return render_template('meal_planning/edit.html', form=form, meal_plan=meal_plan)

@meal_planning_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a meal plan entry"""
    meal_plan = MealPlan.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(meal_plan)
    db.session.commit()
    flash('Meal removed from plan!', 'success')
    return redirect(url_for('meal_planning.index'))

@meal_planning_bp.route('/<int:id>/cook', methods=['POST'])
@login_required
def cook_meal(id):
    """Mark a meal as cooked and update inventory"""
    meal_plan = MealPlan.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if not meal_plan.recipe:
        flash('Cannot cook custom meal without recipe', 'error')
        return redirect(url_for('meal_planning.index'))
    
    try:
        # Update inventory based on recipe ingredients
        ingredients = meal_plan.recipe.get_ingredients()
        for ingredient_line in ingredients:
            # Simple parsing - assumes format like "1 cup rice" or "2 tbsp oil"
            parts = ingredient_line.strip().split()
            if len(parts) >= 3:
                try:
                    quantity = float(parts[0])
                    unit = parts[1]
                    item_name = ' '.join(parts[2:])
                    
                    # Adjust quantity based on servings
                    adjusted_quantity = quantity * (meal_plan.servings / meal_plan.recipe.servings)
                    
                    # Find matching inventory item
                    inventory_item = InventoryItem.query.filter_by(
                        user_id=current_user.id,
                        name=item_name
                    ).first()
                    
                    if inventory_item:
                        # Reduce quantity
                        new_quantity = max(0, inventory_item.quantity - adjusted_quantity)
                        inventory_item.quantity = new_quantity
                        
                except ValueError:
                    # Skip if quantity can't be parsed
                    continue
        
        # Mark meal as cooked
        meal_plan.is_cooked = True
        db.session.commit()
        
        flash(f'Meal "{meal_plan.recipe.name if meal_plan.recipe else meal_plan.custom_meal_name}" marked as cooked! Inventory updated.', 'success')
        
    except Exception as e:
        flash(f'Error updating inventory: {str(e)}', 'error')
    
    return redirect(url_for('meal_planning.index'))

@meal_planning_bp.route('/shopping-list')
@login_required
def shopping_list():
    """Generate shopping list based on meal plans"""
    # Get meal plans for the next 7 days
    start_date = date.today()
    end_date = start_date + timedelta(days=7)
    
    meal_plans = MealPlan.query.filter(
        MealPlan.user_id == current_user.id,
        MealPlan.date >= start_date,
        MealPlan.date <= end_date,
        MealPlan.is_cooked == False
    ).all()
    
    # Calculate required ingredients
    required_ingredients = {}
    for meal_plan in meal_plans:
        if meal_plan.recipe:
            ingredients = meal_plan.recipe.get_ingredients()
            for ingredient_line in ingredients:
                parts = ingredient_line.strip().split()
                if len(parts) >= 3:
                    try:
                        quantity = float(parts[0])
                        unit = parts[1]
                        item_name = ' '.join(parts[2:])
                        
                        # Adjust quantity based on servings
                        adjusted_quantity = quantity * (meal_plan.servings / meal_plan.recipe.servings)
                        
                        if item_name in required_ingredients:
                            required_ingredients[item_name]['quantity'] += adjusted_quantity
                        else:
                            required_ingredients[item_name] = {
                                'quantity': adjusted_quantity,
                                'unit': unit
                            }
                    except ValueError:
                        continue
    
    # Check against current inventory
    shopping_items = []
    for item_name, required in required_ingredients.items():
        inventory_item = InventoryItem.query.filter_by(
            user_id=current_user.id,
            name=item_name
        ).first()
        
        if inventory_item:
            needed = max(0, required['quantity'] - inventory_item.quantity)
            if needed > 0:
                shopping_items.append({
                    'name': item_name,
                    'needed': needed,
                    'unit': required['unit'],
                    'query': inventory_item.blinkit_query or item_name
                })
        else:
            shopping_items.append({
                'name': item_name,
                'needed': required['quantity'],
                'unit': required['unit'],
                'query': item_name
            })
    
    return render_template('meal_planning/shopping_list.html', shopping_items=shopping_items)

@meal_planning_bp.route('/auto-suggest', methods=['POST'])
@login_required
def auto_suggest_meals():
    """Auto-suggest meals for the week based on available ingredients"""
    try:
        # Get available ingredients
        inventory_items = InventoryItem.query.filter_by(user_id=current_user.id).all()
        available_ingredients = [item.name for item in inventory_items if item.quantity > 0]
        
        if not available_ingredients:
            return jsonify({'error': 'No ingredients available'}), 400
        
        # Find recipes that can be made with available ingredients
        suggested_meals = []
        recipes = Recipe.query.filter_by(user_id=current_user.id).all()
        
        for recipe in recipes:
            recipe_ingredients = [ing.split()[-1] if len(ing.split()) >= 3 else ing for ing in recipe.get_ingredients()]
            # Simple matching - check if most ingredients are available
            available_count = sum(1 for ing in recipe_ingredients if any(avail in ing.lower() for avail in available_ingredients))
            if available_count >= len(recipe_ingredients) * 0.7:  # 70% of ingredients available
                suggested_meals.append({
                    'recipe_id': recipe.id,
                    'name': recipe.name,
                    'category': recipe.category,
                    'available_ingredients': available_count,
                    'total_ingredients': len(recipe_ingredients)
                })
        
        return jsonify({'suggested_meals': suggested_meals})
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate suggestions: {str(e)}'}), 500

