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

@bp.route('/view_group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def view_group(group_id):
    group = Group.get(group_id)

    if not group:
        return "Group not found", 404
    if request.method == 'POST':
        try:
            if 'toggle_likes' in request.form and group.owner_id == current_user.id:
                new_state = not group.submit_likes
                Group.turn_on_likes(group_id, new_state)
                flash(f"{'Enabled' if new_state else 'Disabled'} likes for the group.", "success")
                return redirect(url_for('groups.view_group', group_id=group_id))
            if 'remove_member' in request.form and group.owner_id == current_user.id:
                member_id = int(request.form.get('remove_member'))
                if Group.remove_member(group_id, member_id):
                    flash("Member removed successfully.", "success")
                else:
                    flash("Failed to remove member. Ensure the member exists in the group.", "danger")
            if 'like_member' in request.form:
                liked_user_id = int(request.form.get('like_member'))
                action = Group.toggle_like_member(group_id, current_user.id, liked_user_id)
                flash(f"You have {action} this member.", "success")
        except ValueError as e:
            flash(f"Invalid input: {str(e)}", "danger")
        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}", "danger")

    # Get group details and members
    group_members = Group.get_members(group_id, current_user.id)
    return render_template(
        'view_group.html',
        members=group_members,
        group=group,
        is_owner=(group.owner_id == current_user.id),
        title="View Group"
    )


@bp.route('/groups/<int:group_id>/join', methods=['POST'])
def join_group(group_id):
    success = Group.join_group(group_id, current_user.id, request.form.get('password'))
    if success:
        return redirect(url_for(f"groups.view_group", group_id=group_id))
    print("Fail")

@login_required
@bp.route('/groups/<int:group_id>/leave', methods=['POST'])
def leave_group(group_id):
    group = Group.get(group_id)
    if not group:
        print("Group not found.", "danger")
        return redirect(url_for('groups.index'))
    if group.owner_id == current_user.id:
        print("You cannot leave a group you own.", "danger")
        return redirect(url_for('groups.view_group', group_id=group_id))
    if Group.leave_group(group_id, current_user.id):
        print("You have successfully left the group.", "success")
    else:
        print("Failed to leave the group.", "danger")
    return redirect(url_for('index.index'))


@login_required
@bp.route('/groups/<int:group_id>/generate_matches', methods=['GET'])
def generate_matches(group_id):
    group = Group.get(group_id)
    if not group:
        return "Group not found"
    if group.owner_id != current_user.id:
        return "Only the group owner can generate matches."
    matches = Group.generate_matches(group_id)
    for match in matches:
        if((match[1],match[0]) in matches and match[0]<match[1]):
            print(match)
    return "Matches generated. Check server logs for results."