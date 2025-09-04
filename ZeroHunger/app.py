import os
import logging
from flask import Flask
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# Import models and create in-memory storage
from models import users, foods, requests as food_requests, get_user_by_id

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

# Register blueprints
from auth import auth_bp
from provider import provider_bp
from receiver import receiver_bp
from delivery import delivery_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(provider_bp, url_prefix='/provider')
app.register_blueprint(receiver_bp, url_prefix='/receiver')
app.register_blueprint(delivery_bp, url_prefix='/delivery')

# Main routes
from flask import render_template, redirect, url_for
from flask_login import current_user, login_required

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.current_role == 'provider':
            return redirect(url_for('provider.dashboard'))
        else:
            return redirect(url_for('receiver.dashboard'))
    return render_template('index.html')

@app.route('/switch_role/<role>')
@login_required
def switch_role(role):
    if role in ['provider', 'receiver', 'delivery_person']:
        current_user.current_role = role
        app.logger.info(f"User {current_user.username} switched to role: {role}")
        
        if role == 'provider':
            return redirect(url_for('provider.dashboard'))
        elif role == 'delivery_person':
            return redirect(url_for('delivery.dashboard'))
        else:
            return redirect(url_for('receiver.dashboard'))
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
