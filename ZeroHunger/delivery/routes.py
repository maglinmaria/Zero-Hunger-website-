from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import delivery_bp
from models import (get_available_requests_for_delivery, assign_delivery_person, 
                   get_assignments_by_delivery_person, get_assignment_by_id, 
                   verify_otp, get_food_by_id, requests)

@delivery_bp.route('/dashboard')
@login_required
def dashboard():
    # Get delivery person's assignments
    assignments = get_assignments_by_delivery_person(current_user.id)
    
    # Get assignment details with food info
    assignments_with_details = []
    for assignment in assignments:
        request_obj = requests.get(assignment.request_id)
        if request_obj:
            food = get_food_by_id(request_obj.food_id)
            assignments_with_details.append({
                'assignment': assignment,
                'request': request_obj,
                'food': food
            })
    
    # Get available requests for pickup
    available_requests = get_available_requests_for_delivery()
    available_with_food = []
    for req in available_requests[:5]:  # Show top 5
        food = get_food_by_id(req.food_id)
        if food:
            available_with_food.append({
                'request': req,
                'food': food
            })
    
    return render_template('delivery/dashboard.html', 
                         assignments=assignments_with_details,
                         available_requests=available_with_food)

@delivery_bp.route('/available_requests')
@login_required
def available_requests():
    # Get filter parameters
    location_filter = request.args.get('location', '').strip()
    
    # Get available requests
    if location_filter:
        available_requests = get_available_requests_for_delivery(location_filter)
    else:
        available_requests = get_available_requests_for_delivery()
    
    # Add food details
    requests_with_food = []
    for req in available_requests:
        food = get_food_by_id(req.food_id)
        if food:
            requests_with_food.append({
                'request': req,
                'food': food
            })
    
    # Get unique locations for filter
    all_requests = get_available_requests_for_delivery()
    locations = []
    for req in all_requests:
        food = get_food_by_id(req.food_id)
        if food and food.location not in locations:
            locations.append(food.location)
    locations.sort()
    
    return render_template('delivery/available_requests.html', 
                         requests=requests_with_food,
                         locations=locations,
                         current_location=location_filter)

@delivery_bp.route('/accept_request/<request_id>')
@login_required
def accept_request(request_id):
    assignment = assign_delivery_person(request_id, current_user.id)
    
    if assignment:
        flash('Request accepted! Check your dashboard for pickup details.', 'success')
    else:
        flash('Unable to accept this request. It may have been already assigned.', 'error')
    
    return redirect(url_for('delivery.dashboard'))

@delivery_bp.route('/verify_pickup/<assignment_id>', methods=['GET', 'POST'])
@login_required
def verify_pickup(assignment_id):
    assignment = get_assignment_by_id(assignment_id)
    
    if not assignment or assignment.delivery_person_id != current_user.id:
        flash('Assignment not found.', 'error')
        return redirect(url_for('delivery.dashboard'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp_code')
        
        if verify_otp(assignment_id, otp_code, 'pickup'):
            flash('Pickup verified successfully! You can now deliver the food.', 'success')
            return redirect(url_for('delivery.dashboard'))
        else:
            flash('Invalid OTP. Please try again.', 'error')
    
    # Get request and food details
    request_obj = requests.get(assignment.request_id)
    food = get_food_by_id(request_obj.food_id) if request_obj else None
    
    return render_template('delivery/verify_pickup.html', 
                         assignment=assignment,
                         request=request_obj,
                         food=food)

@delivery_bp.route('/verify_delivery/<assignment_id>', methods=['GET', 'POST'])
@login_required
def verify_delivery(assignment_id):
    assignment = get_assignment_by_id(assignment_id)
    
    if not assignment or assignment.delivery_person_id != current_user.id:
        flash('Assignment not found.', 'error')
        return redirect(url_for('delivery.dashboard'))
    
    if assignment.status != 'picked_up':
        flash('You must pick up the food first before delivery.', 'error')
        return redirect(url_for('delivery.dashboard'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp_code')
        
        if verify_otp(assignment_id, otp_code, 'delivery'):
            flash('Delivery completed successfully! Thank you for your service.', 'success')
            return redirect(url_for('delivery.dashboard'))
        else:
            flash('Invalid OTP. Please try again.', 'error')
    
    # Get request and food details
    request_obj = requests.get(assignment.request_id)
    food = get_food_by_id(request_obj.food_id) if request_obj else None
    
    return render_template('delivery/verify_delivery.html', 
                         assignment=assignment,
                         request=request_obj,
                         food=food)