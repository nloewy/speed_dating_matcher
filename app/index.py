from flask import render_template
from flask_login import current_user
import datetime

from flask import Blueprint
bp = Blueprint('index', __name__)

from .model.user import User

@bp.route('/')
def index():
    # get all available products for sale:
    return render_template('index.html',
                           user=User.get_all())
