from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp
from flask import render_template, redirect, url_for, flash, request

class CreateGroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired()])
    description = StringField('Group Description')
    password = PasswordField('Group Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Group Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Create Group')

from .model.group import Group


from flask import Blueprint
bp = Blueprint('groups', __name__)

@bp.route('/create_group', methods=['GET', 'POST'])
def create_group():
    form = CreateGroupForm()
    if form.validate_on_submit():
        group_id = Group.create_group(form.name.data, form.description.data,
                         form.password.data, current_user.id)
        if group_id:
            flash('Group Created!')
            return redirect(url_for('index.index'))
    return render_template('create_group.html', title='Create Group', form=form)

"""@bp.route('/groups/<group_id>', methods=['GET'])
def create_group():
    form = CreateGroupForm()
    if form.validate_on_submit():
        group_id = Group.create_group(form.name.data,
                         form.password.data, current_user.id)
        if group_id:
            flash('Group Created!')
            return redirect(url_for('groups/{group_id}'))
    return render_template('create_group.html', title='Create Group', form=form)

"""