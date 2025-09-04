from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from . import auth_bp
from models import get_user_by_username, get_user_by_email, create_user
import logging

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please fill in all fields.', 'error')
            return render_template('auth/login.html')
        
        user = get_user_by_username(username)
        
        if user and user.check_password(password):
            login_user(user)
            logging.info(f'User {username} logged in successfully')
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect based on current role
            if user.current_role == 'provider':
                return redirect(url_for('provider.dashboard'))
            else:
                return redirect(url_for('receiver.dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            logging.warning(f'Failed login attempt for username: {username}')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('Please fill in all fields.', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')
        
        if password and len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('auth/register.html')
        
        # Check if user already exists
        if get_user_by_username(username):
            flash('Username already exists.', 'error')
            return render_template('auth/register.html')
        
        if get_user_by_email(email):
            flash('Email already registered.', 'error')
            return render_template('auth/register.html')
        
        # Create user
        user = create_user(username, email, password)
        login_user(user)
        
        logging.info(f'New user registered: {username}')
        flash(f'Registration successful! Welcome, {username}!', 'success')
        
        return redirect(url_for('receiver.dashboard'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
