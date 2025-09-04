from flask import Blueprint

provider_bp = Blueprint('provider', __name__, template_folder='../templates/provider')

from . import routes
