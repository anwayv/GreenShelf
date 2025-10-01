from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange
from app.models import db, User, Notification
import json

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    family_size = IntegerField('Family Size', validators=[DataRequired(), NumberRange(min=1, max=20)], default=1)
    pincode = StringField('Pincode', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Register')

class PreferencesForm(FlaskForm):
    family_size = IntegerField('Family Size', validators=[NumberRange(min=1, max=20)])
    preferred_brands = TextAreaField('Preferred Brands (one per line)')
    dietary_restrictions = TextAreaField('Dietary Restrictions (one per line)')
    taste_preferences = TextAreaField('Taste Preferences (one per line)')
    delivery_time_slots = TextAreaField('Available Delivery Time Slots (one per line)')
    upi_id = StringField('UPI ID')
    auto_order_enabled = BooleanField('Enable Auto-Ordering')
    checkout_enabled = BooleanField('Proceed to Checkout During Auto-Order')
    check_interval_minutes = IntegerField('Check Interval (minutes)', validators=[NumberRange(min=5, max=1440)], default=60)
    submit = SubmitField('Save Preferences')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            family_size=form.family_size.data,
            pincode=form.pincode.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Create welcome notification
        notification = Notification(
            user_id=user.id,
            title='Welcome to Green Shelf!',
            message='Your account has been created successfully. Complete your profile setup to get started.',
            notification_type='welcome'
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = PreferencesForm()
    
    if request.method == 'GET':
        # Populate form with current user data
        form.family_size.data = current_user.family_size
        form.preferred_brands.data = '\n'.join(current_user.get_preferred_brands())
        form.dietary_restrictions.data = '\n'.join(current_user.get_dietary_restrictions())
        form.taste_preferences.data = '\n'.join(current_user.get_taste_preferences())
        form.delivery_time_slots.data = '\n'.join(current_user.get_delivery_time_slots())
        form.upi_id.data = current_user.upi_id
        form.auto_order_enabled.data = current_user.auto_order_enabled
        form.checkout_enabled.data = current_user.checkout_enabled
        form.check_interval_minutes.data = current_user.check_interval_minutes
    
    if form.validate_on_submit():
        # Update user preferences
        current_user.family_size = form.family_size.data
        current_user.set_preferred_brands([b.strip() for b in form.preferred_brands.data.split('\n') if b.strip()])
        current_user.set_dietary_restrictions([r.strip() for r in form.dietary_restrictions.data.split('\n') if r.strip()])
        current_user.set_taste_preferences([p.strip() for p in form.taste_preferences.data.split('\n') if p.strip()])
        current_user.set_delivery_time_slots([s.strip() for s in form.delivery_time_slots.data.split('\n') if s.strip()])
        current_user.upi_id = form.upi_id.data
        current_user.auto_order_enabled = form.auto_order_enabled.data
        current_user.checkout_enabled = form.checkout_enabled.data
        current_user.check_interval_minutes = form.check_interval_minutes.data
        
        db.session.commit()
        flash('Preferences updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', title='Profile', form=form)

@auth_bp.route('/onboarding')
@login_required
def onboarding():
    """Onboarding flow for new users"""
    return render_template('auth/onboarding.html', title='Setup Your Green Shelf')

@auth_bp.route('/capture-cookies', methods=['POST'])
@login_required
def capture_cookies():
    """Endpoint to receive Blinkit cookies from frontend"""
    try:
        cookies_data = request.json.get('cookies', {})
        current_user.blinkit_cookies = json.dumps(cookies_data)
        db.session.commit()
        
        # Create notification
        notification = Notification(
            user_id=current_user.id,
            title='Blinkit Integration Complete',
            message='Your Blinkit account has been successfully linked for automated ordering.',
            notification_type='integration'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Cookies captured successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

