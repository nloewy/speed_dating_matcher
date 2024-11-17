from flask import render_template
from flask_login import current_user, login_required
import datetime

from flask import Blueprint
bp = Blueprint('index', __name__)

from .model.user import User
from .model.group import Group

@bp.route('/')
def index():
    # get all available products for sale:
    return render_template('index.html',
                           users=User.get_all(), groups=Group.get_all())

