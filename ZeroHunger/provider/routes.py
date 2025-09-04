import os
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import provider_bp
from models import create_food, get_foods_by_provider, FOOD_CATEGORIES, get_requests_by_provider, get_food_by_id
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@provider_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's uploaded foods
    user_foods = get_foods_by_provider(current_user.id)
    
    # Get requests for user's foods
    food_requests = get_requests_by_provider(current_user.id)
    
    # Statistics
    total_foods = len(user_foods)
    available_foods = len([f for f in user_foods if f.status == 'available'])
    booked_foods = len([f for f in user_foods if f.status == 'booked'])
    
    return render_template('provider/dashboard.html', 
                         foods=user_foods,
                         requests=food_requests,
                         total_foods=total_foods,
                         available_foods=available_foods,
                         booked_foods=booked_foods)

@provider_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_food():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        expiry_hours = request.form.get('expiry_hours')
        location = request.form.get('location')
        
        # Validation
        if not all([title, description, category, expiry_hours, location]):
            flash('Please fill in all required fields.', 'error')
            return render_template('provider/upload.html', categories=FOOD_CATEGORIES)
        
        try:
            expiry_hours = int(expiry_hours) if expiry_hours else 0
            if expiry_hours <= 0:
                raise ValueError("Expiry hours must be positive")
        except (ValueError, TypeError):
            flash('Please enter a valid expiry time in hours.', 'error')
            return render_template('provider/upload.html', categories=FOOD_CATEGORIES)
        
        if category not in FOOD_CATEGORIES:
            flash('Please select a valid category.', 'error')
            return render_template('provider/upload.html', categories=FOOD_CATEGORIES)
        
        # Handle file upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                if file.filename and allowed_file(file.filename):
                    # Generate unique filename
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                    
                    try:
                        file.save(file_path)
                        image_filename = unique_filename
                        current_app.logger.info(f'File uploaded successfully: {unique_filename}')
                    except Exception as e:
                        current_app.logger.error(f'Error saving file: {e}')
                        flash('Error uploading image. Please try again.', 'error')
                        return render_template('provider/upload.html', categories=FOOD_CATEGORIES)
                else:
                    flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WEBP files.', 'error')
                    return render_template('provider/upload.html', categories=FOOD_CATEGORIES)
        
        # Create food item
        food = create_food(title, description, category, expiry_hours, location, current_user.id, image_filename)
        
        current_app.logger.info(f'Food item created: {food.title} by {current_user.username}')
        flash('Food item uploaded successfully!', 'success')
        return redirect(url_for('provider.dashboard'))
    
    return render_template('provider/upload.html', categories=FOOD_CATEGORIES)

@provider_bp.route('/food/<food_id>')
@login_required
def view_food(food_id):
    food = get_food_by_id(food_id)
    
    if not food or food.provider_id != current_user.id:
        flash('Food item not found.', 'error')
        return redirect(url_for('provider.dashboard'))
    
    return render_template('provider/food_detail.html', food=food)

@provider_bp.route('/complete/<food_id>')
@login_required
def complete_food(food_id):
    food = get_food_by_id(food_id)
    
    if not food or food.provider_id != current_user.id:
        flash('Food item not found.', 'error')
        return redirect(url_for('provider.dashboard'))
    
    if food.status != 'booked':
        flash('Only booked food items can be marked as completed.', 'error')
        return redirect(url_for('provider.dashboard'))
    
    food.status = 'completed'
    flash('Food delivery marked as completed!', 'success')
    return redirect(url_for('provider.dashboard'))
