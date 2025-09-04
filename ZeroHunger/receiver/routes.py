from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import receiver_bp
from models import (get_available_foods, get_foods_by_location, get_foods_by_category, 
                   request_food, get_requests_by_receiver, get_food_by_id, FOOD_CATEGORIES,
                   get_assignments_by_delivery_person, delivery_assignments)

@receiver_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's requests
    user_requests = get_requests_by_receiver(current_user.id)
    
    # Get food details for each request with delivery info
    requests_with_food = []
    for req in user_requests:
        food = get_food_by_id(req.food_id)
        if food:
            # Find delivery assignment if any
            delivery_assignment = None
            for assignment in delivery_assignments.values():
                if assignment.request_id == req.id:
                    delivery_assignment = assignment
                    break
            
            requests_with_food.append({
                'request': req,
                'food': food,
                'delivery_assignment': delivery_assignment
            })
    
    # Recent available foods
    recent_foods = get_available_foods()[:6]  # Show 6 most recent
    
    return render_template('receiver/dashboard.html', 
                         requests=requests_with_food,
                         recent_foods=recent_foods)

@receiver_bp.route('/browse')
@login_required
def browse_food():
    # Get filter parameters
    location_filter = request.args.get('location', '').strip()
    category_filter = request.args.get('category', '').strip()
    
    # Get foods based on filters
    if location_filter and category_filter:
        # Both filters applied
        foods = [f for f in get_available_foods() 
                if f.location.lower() == location_filter.lower() 
                and f.category.lower() == category_filter.lower()]
    elif location_filter:
        # Location filter only
        foods = get_foods_by_location(location_filter)
    elif category_filter:
        # Category filter only
        foods = get_foods_by_category(category_filter)
    else:
        # No filters
        foods = get_available_foods()
    
    # Get unique locations for filter dropdown
    all_foods = get_available_foods()
    locations = list(set([food.location for food in all_foods]))
    locations.sort()
    
    return render_template('receiver/browse.html', 
                         foods=foods,
                         categories=FOOD_CATEGORIES,
                         locations=locations,
                         current_location=location_filter,
                         current_category=category_filter)

@receiver_bp.route('/request/<food_id>', methods=['GET', 'POST'])
@login_required
def request_food_item(food_id):
    food = get_food_by_id(food_id)
    
    if not food:
        flash('Food item not found.', 'error')
        return redirect(url_for('receiver.browse_food'))
    
    if food.status != 'available':
        flash('This food item is no longer available.', 'error')
        return redirect(url_for('receiver.browse_food'))
    
    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        
        # Create request
        food_request = request_food(food_id, current_user.id, message)
        
        if food_request:
            flash('Food request sent successfully! The provider will be notified.', 'success')
            return redirect(url_for('receiver.dashboard'))
        else:
            flash('Unable to request this food item. It may have been claimed by someone else.', 'error')
    
    return render_template('receiver/request_form.html', food=food)

@receiver_bp.route('/food/<food_id>')
@login_required
def view_food(food_id):
    food = get_food_by_id(food_id)
    
    if not food:
        flash('Food item not found.', 'error')
        return redirect(url_for('receiver.browse_food'))
    
    return render_template('receiver/food_detail.html', food=food)
