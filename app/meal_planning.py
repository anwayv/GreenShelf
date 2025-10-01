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

@meal_planning_bp.route('/check-inventory', methods=['POST'])
@login_required
def check_inventory():
    """Check ingredient availability for a recipe"""
    try:
        data = request.get_json()
        recipe_id = data.get('recipe_id')
        servings = data.get('servings', 1)
        
        if not recipe_id:
            return jsonify({'error': 'Recipe ID required'}), 400
        
        recipe = Recipe.query.get_or_404(recipe_id)
        if recipe.user_id != current_user.id:
            return jsonify({'error': 'Recipe not found'}), 404
        
        ingredients = recipe.get_ingredients()
        ingredient_status = []
        
        for ingredient_line in ingredients:
            parts = ingredient_line.strip().split()
            if len(parts) >= 3:
                try:
                    quantity = float(parts[0])
                    unit = parts[1]
                    item_name = ' '.join(parts[2:])
                    
                    # Adjust quantity based on servings
                    needed_quantity = quantity * (servings / recipe.servings)
                    
                    # Find matching inventory item
                    inventory_item = InventoryItem.query.filter_by(
                        user_id=current_user.id,
                        name=item_name
                    ).first()
                    
                    if inventory_item:
                        current_quantity = inventory_item.quantity
                        if current_quantity >= needed_quantity:
                            status = 'available'
                        elif current_quantity > 0:
                            status = 'low'
                        else:
                            status = 'missing'
                    else:
                        current_quantity = 0
                        status = 'missing'
                    
                    ingredient_status.append({
                        'name': item_name,
                        'needed': needed_quantity,
                        'current_quantity': current_quantity,
                        'unit': unit,
                        'status': status
                    })
                    
                except ValueError:
                    continue
        
        return jsonify({'ingredients': ingredient_status})
        
    except Exception as e:
        return jsonify({'error': f'Failed to check inventory: {str(e)}'}), 500

@meal_planning_bp.route('/auto-order', methods=['POST'])
@login_required
def auto_order():
    """Auto-order missing ingredients"""
    try:
        data = request.get_json()
        item_name = data.get('item_name')
        quantity = data.get('quantity')
        unit = data.get('unit')
        
        if not all([item_name, quantity, unit]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if auto-ordering is enabled
        if not current_user.auto_order_enabled:
            return jsonify({'error': 'Auto-ordering is not enabled'}), 400
        
        # Find or create inventory item
        inventory_item = InventoryItem.query.filter_by(
            user_id=current_user.id,
            name=item_name
        ).first()
        
        if not inventory_item:
            inventory_item = InventoryItem(
                user_id=current_user.id,
                name=item_name,
                quantity=0,
                unit=unit,
                blinkit_query=item_name
            )
            db.session.add(inventory_item)
        
        # Create order record
        order_items = [{
            'name': item_name,
            'quantity': quantity,
            'unit': unit,
            'query': inventory_item.blinkit_query or item_name
        }]
        
        order = Order(
            user_id=current_user.id,
            status='pending'
        )
        order.set_items(order_items)
        db.session.add(order)
        
        # Here you would integrate with the bot system to actually place the order
        # For now, we'll just simulate the process
        
        try:
            # Import the bot functionality
            from bot.green_shelf_bot import place_order_via_bot
            
            # Place order through bot
            success = place_order_via_bot(
                user_id=current_user.id,
                items=order_items
            )
            
            if success:
                order.status = 'placed'
                flash(f'Successfully ordered {quantity} {unit} of {item_name}!', 'success')
            else:
                order.status = 'failed'
                flash(f'Failed to order {item_name}. Please try manually.', 'error')
                
        except ImportError:
            # Bot not available, mark as pending
            order.status = 'pending'
            flash(f'{item_name} added to pending orders. Enable auto-checkout to complete.', 'info')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Order placed for {item_name}'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to place order: {str(e)}'}), 500

@meal_planning_bp.route('/auto-order-bulk', methods=['POST'])
@login_required
def auto_order_bulk():
    """Auto-order multiple items at once"""
    try:
        data = request.get_json()
        items = data.get('items', [])
        
        if not items:
            return jsonify({'error': 'No items provided'}), 400
        
        # Check if auto-ordering is enabled
        if not current_user.auto_order_enabled:
            return jsonify({'error': 'Auto-ordering is not enabled'}), 400
        
        order_items = []
        
        for item_data in items:
            item_name = item_data.get('item_name')
            quantity = item_data.get('quantity')
            unit = item_data.get('unit')
            query = item_data.get('query', item_name)
            
            if not all([item_name, quantity, unit]):
                continue
            
            # Find or create inventory item
            inventory_item = InventoryItem.query.filter_by(
                user_id=current_user.id,
                name=item_name
            ).first()
            
            if not inventory_item:
                inventory_item = InventoryItem(
                    user_id=current_user.id,
                    name=item_name,
                    quantity=0,
                    unit=unit,
                    blinkit_query=query
                )
                db.session.add(inventory_item)
            
            order_items.append({
                'name': item_name,
                'quantity': quantity,
                'unit': unit,
                'query': query
            })
        
        if not order_items:
            return jsonify({'error': 'No valid items to order'}), 400
        
        # Create order record
        order = Order(
            user_id=current_user.id,
            status='pending'
        )
        order.set_items(order_items)
        db.session.add(order)
        
        # Try to place order through bot
        try:
            from bot.green_shelf_bot import place_order_via_bot
            
            success = place_order_via_bot(
                user_id=current_user.id,
                items=order_items
            )
            
            if success:
                order.status = 'placed'
                flash(f'Successfully ordered {len(order_items)} items!', 'success')
            else:
                order.status = 'failed'
                flash(f'Failed to order items. Please try manually.', 'error')
                
        except ImportError:
            order.status = 'pending'
            flash(f'{len(order_items)} items added to pending orders.', 'info')
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Successfully ordered {len(order_items)} items',
            'order_id': order.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to place bulk order: {str(e)}'}), 500

