from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from threading import Thread, Event
import time
import json
import os
from pathlib import Path
from config import Config
from app.models import db, User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    csrf = CSRFProtect(app)
    
    # Setup login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create upload directory
    upload_dir = Path(app.config['UPLOAD_FOLDER'])
    upload_dir.mkdir(exist_ok=True)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from app.routes import main
    from app.auth import auth_bp
    from app.recipes import recipes_bp
    from app.meal_planning import meal_planning_bp
    from app.receipts import receipts_bp
    
    app.register_blueprint(main)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(recipes_bp, url_prefix='/recipes')
    app.register_blueprint(meal_planning_bp, url_prefix='/meal-planning')
    app.register_blueprint(receipts_bp, url_prefix='/receipts')

    # Background auto-order scheduler
    stop_event = Event()

    def run_scheduler():
        from bot.green_shelf_bot import GreenShelfBot
        while not stop_event.is_set():
            try:
                # Create application context for database operations
                with app.app_context():
                    # Get all users with auto-order enabled
                    users = User.query.filter_by(auto_order_enabled=True).all()
                    for user in users:
                        if user.upi_id:
                            # Check for low stock items
                            low_stock_items = []
                            for item in user.inventory_items:
                                if item.is_low_stock():
                                    low_stock_items.append(item.blinkit_query or item.name)
                            
                            if low_stock_items:
                                try:
                                    bot = GreenShelfBot(user.upi_id, user_id=user.id)
                                    bot.process_items(low_stock_items)
                                    if user.checkout_enabled:
                                        bot.proceed_to_checkout_and_select_upi(user.upi_id)
                                except Exception as e:
                                    print(f"Auto-order failed for user {user.id}: {e}")
                
                # Sleep for the minimum interval among all users
                min_interval = 60  # default 1 hour
                with app.app_context():
                    users = User.query.filter_by(auto_order_enabled=True).all()
                    for user in users:
                        if user.check_interval_minutes:
                            min_interval = min(min_interval, user.check_interval_minutes)
                
                # Sleep in 1-second steps to allow quick shutdown
                for _ in range(min_interval * 60):
                    if stop_event.is_set():
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Scheduler error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

    # Start the scheduler thread in daemon mode so it doesn't block exit
    t = Thread(target=run_scheduler, daemon=True)
    t.start()

    return app
