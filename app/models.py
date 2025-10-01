from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User preferences
    family_size = db.Column(db.Integer, default=1)
    preferred_brands = db.Column(db.Text)  # JSON string
    dietary_restrictions = db.Column(db.Text)  # JSON string
    taste_preferences = db.Column(db.Text)  # JSON string
    delivery_time_slots = db.Column(db.Text)  # JSON string
    upi_id = db.Column(db.String(100))
    auto_order_enabled = db.Column(db.Boolean, default=False)
    checkout_enabled = db.Column(db.Boolean, default=False)
    check_interval_minutes = db.Column(db.Integer, default=60)
    
    # Blinkit integration
    blinkit_cookies = db.Column(db.Text)  # JSON string
    pincode = db.Column(db.String(10))
    cookies_saved = db.Column(db.Boolean, default=False)
    
    # Relationships
    inventory_items = db.relationship('InventoryItem', backref='user', lazy=True, cascade='all, delete-orphan')
    meal_plans = db.relationship('MealPlan', backref='user', lazy=True, cascade='all, delete-orphan')
    recipes = db.relationship('Recipe', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_preferred_brands(self):
        try:
            return json.loads(self.preferred_brands) if self.preferred_brands else []
        except:
            return []
    
    def set_preferred_brands(self, brands):
        self.preferred_brands = json.dumps(brands)
    
    def get_dietary_restrictions(self):
        try:
            return json.loads(self.dietary_restrictions) if self.dietary_restrictions else []
        except:
            return []
    
    def set_dietary_restrictions(self, restrictions):
        self.dietary_restrictions = json.dumps(restrictions)
    
    def get_taste_preferences(self):
        try:
            return json.loads(self.taste_preferences) if self.taste_preferences else []
        except:
            return []
    
    def set_taste_preferences(self, preferences):
        self.taste_preferences = json.dumps(preferences)
    
    def get_delivery_time_slots(self):
        try:
            return json.loads(self.delivery_time_slots) if self.delivery_time_slots else []
        except:
            return []
    
    def set_delivery_time_slots(self, slots):
        self.delivery_time_slots = json.dumps(slots)

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, default=0.0)
    threshold = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(20), default='pcs')
    blinkit_query = db.Column(db.String(200))
    category = db.Column(db.String(50))  # e.g., 'dairy', 'vegetables', 'spices'
    brand_preference = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_low_stock(self):
        return self.quantity < self.threshold

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    ingredients = db.Column(db.Text)  # JSON string
    instructions = db.Column(db.Text)
    prep_time = db.Column(db.Integer)  # minutes
    cook_time = db.Column(db.Integer)  # minutes
    servings = db.Column(db.Integer, default=1)
    category = db.Column(db.String(50))  # e.g., 'breakfast', 'lunch', 'dinner', 'snack'
    difficulty = db.Column(db.String(20))  # 'easy', 'medium', 'hard'
    tags = db.Column(db.Text)  # JSON string
    is_ai_generated = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_ingredients(self):
        try:
            return json.loads(self.ingredients) if self.ingredients else []
        except:
            return []
    
    def set_ingredients(self, ingredients):
        self.ingredients = json.dumps(ingredients)
    
    def get_tags(self):
        try:
            return json.loads(self.tags) if self.tags else []
        except:
            return []
    
    def set_tags(self, tags):
        self.tags = json.dumps(tags)

class MealPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # 'breakfast', 'lunch', 'dinner', 'snack'
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    custom_meal_name = db.Column(db.String(200))
    servings = db.Column(db.Integer, default=1)
    is_cooked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    recipe = db.relationship('Recipe', backref='meal_plans')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.Column(db.Text)  # JSON string of items ordered
    total_amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'placed', 'delivered', 'cancelled'
    blinkit_order_id = db.Column(db.String(100))
    delivery_date = db.Column(db.Date)
    delivery_time_slot = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_items(self):
        try:
            return json.loads(self.items) if self.items else []
        except:
            return []
    
    def set_items(self, items):
        self.items = json.dumps(items)

class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    extracted_text = db.Column(db.Text)
    parsed_items = db.Column(db.Text)  # JSON string
    total_amount = db.Column(db.Float)
    store_name = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    is_processed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_parsed_items(self):
        try:
            return json.loads(self.parsed_items) if self.parsed_items else []
        except:
            return []
    
    def set_parsed_items(self, items):
        self.parsed_items = json.dumps(items)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))  # 'order', 'reminder', 'low_stock', 'recipe'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

