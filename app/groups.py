from flask_login import login_user, logout_user, current_user, login_required
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


class JoinGroupForm(FlaskForm):
    password = PasswordField('Group Password', validators=[DataRequired()])
    submit = SubmitField('Join Group')

from .model.group import Group


from flask import Blueprint
bp = Blueprint('groups', __name__)

@login_required
@bp.route('/create_group', methods=['GET', 'POST'])
def create_group():
    form = CreateGroupForm()
    if form.validate_on_submit():
        group_id = Group.create_group(form.name.data, form.description.data,
                         form.password.data, current_user.id)
        if group_id:
            return redirect(url_for('index.index'))
    return render_template('create_group.html', title='Create Group', form=form)

@login_required
@bp.route('/view_group/<int:group_id>', methods=['GET', 'POST'])
def view_group(group_id):
    if not Group.user_in_group(current_user.id, group_id):
        form = JoinGroupForm()
        if form.validate_on_submit():
            if Group.join_group(group_id, current_user.id, form.password.data):
                return render_template('view_group.html', form = form, title='View Group')
    group_members = Group.get_members(group_id)
    group = Group.get(group_id)
    return render_template('view_group.html', members = group_members, group = group, title='View Group')
