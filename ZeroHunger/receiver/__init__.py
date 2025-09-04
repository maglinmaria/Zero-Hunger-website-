from flask import Blueprint

receiver_bp = Blueprint('receiver', __name__, template_folder='../templates/receiver')

from . import routes
