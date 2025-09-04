from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
import random
import string

# In-memory storage for MVP
users = {}
foods = {}
requests = {}
delivery_assignments = {}
otps = {}

class User(UserMixin):
    def __init__(self, username, email, password):
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.current_role = 'receiver'  # Default role
        self.created_at = datetime.utcnow()
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return self.id

class Food:
    def __init__(self, title, description, category, expiry_hours, location, provider_id, image_filename=None):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.category = category
        self.expiry_hours = expiry_hours
        self.location = location
        self.provider_id = provider_id
        self.image_filename = image_filename
        self.status = 'available'  # available, booked, completed
        self.created_at = datetime.utcnow()
        self.requested_by = None
        self.requested_at = None

class FoodRequest:
    def __init__(self, food_id, receiver_id, message=""):
        self.id = str(uuid.uuid4())
        self.food_id = food_id
        self.receiver_id = receiver_id
        self.message = message
        self.status = 'pending'  # pending, accepted, assigned_for_delivery, delivered
        self.created_at = datetime.utcnow()
        self.assigned_delivery_person = None
        self.delivery_otp = None

class DeliveryAssignment:
    def __init__(self, request_id, delivery_person_id):
        self.id = str(uuid.uuid4())
        self.request_id = request_id
        self.delivery_person_id = delivery_person_id
        self.status = 'assigned'  # assigned, picked_up, delivered
        self.created_at = datetime.utcnow()
        self.pickup_otp = self.generate_otp()
        self.delivery_otp = self.generate_otp()
        self.picked_up_at = None
        self.delivered_at = None
    
    def generate_otp(self):
        return ''.join(random.choices(string.digits, k=6))

class OTP:
    def __init__(self, request_id, otp_type, code):
        self.id = str(uuid.uuid4())
        self.request_id = request_id
        self.otp_type = otp_type  # 'pickup' or 'delivery'
        self.code = code
        self.created_at = datetime.utcnow()
        self.is_used = False

# Helper functions
def get_user_by_id(user_id):
    return users.get(str(user_id))

def get_user_by_username(username):
    for user in users.values():
        if user.username == username:
            return user
    return None

def get_user_by_email(email):
    for user in users.values():
        if user.email == email:
            return user
    return None

def create_user(username, email, password):
    user = User(username, email, password)
    users[user.id] = user
    return user

def create_food(title, description, category, expiry_hours, location, provider_id, image_filename=None):
    food = Food(title, description, category, expiry_hours, location, provider_id, image_filename)
    foods[food.id] = food
    return food

def get_foods_by_provider(provider_id):
    return [food for food in foods.values() if food.provider_id == provider_id]

def get_available_foods():
    return [food for food in foods.values() if food.status == 'available']

def get_foods_by_location(location):
    return [food for food in foods.values() if food.location.lower() == location.lower() and food.status == 'available']

def get_foods_by_category(category):
    return [food for food in foods.values() if food.category.lower() == category.lower() and food.status == 'available']

def get_food_by_id(food_id):
    return foods.get(food_id)

def request_food(food_id, receiver_id, message=""):
    food = get_food_by_id(food_id)
    if food and food.status == 'available':
        food.status = 'booked'
        food.requested_by = receiver_id
        food.requested_at = datetime.utcnow()
        
        request = FoodRequest(food_id, receiver_id, message)
        requests[request.id] = request
        return request
    return None

def get_requests_by_receiver(receiver_id):
    return [req for req in requests.values() if req.receiver_id == receiver_id]

def get_requests_by_provider(provider_id):
    provider_foods = get_foods_by_provider(provider_id)
    provider_food_ids = [food.id for food in provider_foods]
    return [req for req in requests.values() if req.food_id in provider_food_ids]

# Delivery helper functions
def assign_delivery_person(request_id, delivery_person_id):
    request = requests.get(request_id)
    if request and request.status == 'pending':
        assignment = DeliveryAssignment(request_id, delivery_person_id)
        delivery_assignments[assignment.id] = assignment
        request.status = 'assigned_for_delivery'
        request.assigned_delivery_person = delivery_person_id
        return assignment
    return None

def get_assignments_by_delivery_person(delivery_person_id):
    return [assignment for assignment in delivery_assignments.values() 
            if assignment.delivery_person_id == delivery_person_id]

def get_available_requests_for_delivery(location=None):
    available_requests = []
    for request in requests.values():
        if request.status == 'pending':
            food = get_food_by_id(request.food_id)
            if food and (location is None or food.location.lower() == location.lower()):
                available_requests.append(request)
    return available_requests

def verify_otp(assignment_id, otp_code, otp_type):
    assignment = delivery_assignments.get(assignment_id)
    if assignment:
        if otp_type == 'pickup' and assignment.pickup_otp == otp_code:
            assignment.status = 'picked_up'
            assignment.picked_up_at = datetime.utcnow()
            return True
        elif otp_type == 'delivery' and assignment.delivery_otp == otp_code:
            assignment.status = 'delivered'
            assignment.delivered_at = datetime.utcnow()
            # Update request status
            request = requests.get(assignment.request_id)
            if request:
                request.status = 'delivered'
            return True
    return False

def get_assignment_by_id(assignment_id):
    return delivery_assignments.get(assignment_id)

# Food categories
FOOD_CATEGORIES = [
    'Rice', 'Bread', 'Vegetables', 'Curry', 'Fruits', 'Snacks', 
    'Dairy', 'Meat', 'Seafood', 'Desserts', 'Beverages', 'Other'
]
