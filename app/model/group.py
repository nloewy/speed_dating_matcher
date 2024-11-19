from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app as app
from flask_login import current_user
from ..model.user import User
from collections import namedtuple
class Group:

    def __init__(self, id, description, name, owner_id, submit_likes):
        self.id = id
        self.name = name
        self.description = description
        self.owner_id = owner_id
        self._owner=None
        self.submit_likes = submit_likes

    @property
    def owner(self):

        if not self._owner:  
            rows = app.db.execute("""SELECT name FROM Users WHERE id = :id """, id=self.owner_id)
            self._owner = rows[0][0]
        return self._owner

    @staticmethod
    def create_group(name, description, password, owner):
        try:
            rows = app.db.execute("""
                INSERT INTO Groups(name, description, password, owner, submit_likes)
                VALUES(:name, :description, :password, :owner, FALSE) RETURNING id
                """,
                name=name, description = description, password=generate_password_hash(password), owner=owner)
        
            return rows[0][0]
        except Exception as e:
            # likely name already in use
            print(f"Group Creation error: {str(e)}")
            return None

    def get_all_given_user(user_id):
        rows = app.db.execute("""
            SELECT groups.id, 
                groups.name, 
                groups.description, 
                groups.owner, 
                groups.submit_likes,
                users.name AS owner_name, 
                (memberingroup.user_id IS NOT NULL) AS in_group
            FROM groups
            JOIN users ON groups.owner = users.id
            LEFT OUTER JOIN memberingroup 
                ON groups.id = memberingroup.group_id AND memberingroup.user_id = :user_id
            ORDER BY in_group DESC
        """, user_id=user_id)


        Group_3 = namedtuple('Group_3', ['id', 'name', 'description', 'owner_id', 'submit_likes', 'owner', 'in_group'])
        print(rows)
        return [Group_3(*row) for row in rows] if rows else None

    @staticmethod
    def get(group_id):
        rows = app.db.execute("""
                SELECT id, name, description, owner, submit_likes FROM groups WHERE id = :group_id
                """, group_id=group_id)
        return Group(*rows[0]) if rows else None

    @staticmethod
    def get_members(group_id, current_user_id):
        print(generate_password_hash("nl"))

        rows = app.db.execute("""
            SELECT users.id, users.name, users.phone, users.email, users.gender,
                EXISTS (
                    SELECT 1
                    FROM Likes
                    WHERE Likes.group_id = :group_id
                        AND Likes.liked_by = :current_user_id
                        AND Likes.liked = users.id
                ) AS is_liked
            FROM users
            JOIN MemberInGroup ON users.id = MemberInGroup.user_id
            WHERE MemberInGroup.group_id = :group_id
        """, group_id=group_id, current_user_id=current_user_id)
        User = namedtuple('user', ['id', 'name', 'phone', 'email', 'gender', 'is_liked'])
        return [User(*row) for row in rows]

    @staticmethod
    def _validate_group_password(id, password):
        print(id, password)
        rows = app.db.execute("""
            SELECT password
            FROM Groups
            WHERE id = :id
            """,
            id=id)
        print(rows[0][0])
        return rows and check_password_hash(rows[0][0], password)

    @staticmethod
    def join_group(group_id, user_id, group_password):
        try:
            if Group._validate_group_password(group_id, group_password):
                app.db.execute("""
                    INSERT INTO MemberInGroup(user_id, group_id)
                    VALUES(:user_id, :group_id)
                    """,
                    user_id=user_id, group_id = group_id)
                return True
            else:
                print(3)
                return False
        except:
            return False

    @staticmethod
    def turn_on_likes(group_id, is_clicked):
        try:
            if current_user.id == Group.get(group_id).owner_id:
                app.db.execute("""
                    UPDATE Groups SET submit_likes = :likes_on_off WHERE id = :group_id """,
                    likes_on_off=is_clicked, group_id = group_id)
        except:
            return None

    @staticmethod
    def user_in_group(user_id, group_id):
        rows = app.db.execute("""
            SELECT user_id FROM memberingroup WHERE user_id=:user_id AND group_id=:group_id
            """, user_id = user_id, group_id=group_id)
        return True if rows else False

    @staticmethod
    def remove_member(group_id, member_id):
        group = Group.get(group_id)
        if group.owner_id == current_user.id:
            if not group:
                raise ValueError("Group not found")
            if group.owner == member_id:
                raise ValueError("Cannot remove the owner of the group")
            app.db.execute("""
                DELETE FROM MemberInGroup
                WHERE group_id = :group_id AND user_id = :member_id;
            """, group_id = group_id, member_id=member_id)
            print(True)
            return True
        return False
    
    @staticmethod
    def toggle_like_member(group_id, liked_by, liked):
        if liked_by == liked:
            raise ValueError("You cannot like or unlike yourself")

        if not Group.user_in_group(liked_by, group_id) or not Group.user_in_group(liked, group_id):
            raise ValueError("Both users must be in the group")
        existing_like = app.db.execute("""
            SELECT 1
            FROM Likes
            WHERE group_id = :group_id AND liked_by = :user_id AND liked = :liked_user_id
        """, group_id=group_id, user_id=liked_by, liked_user_id=liked)
        if existing_like:
            try:
                app.db.execute("""
                    DELETE FROM Likes
                    WHERE group_id = :group_id AND liked_by = :liked_by AND liked = :liked
                """, group_id=group_id, liked_by=liked_by, liked=liked)
                return "unliked"
            except Exception as e:
                raise ValueError("Failed to unlike member") from e
        else:
            try:
                app.db.execute("""
                    INSERT INTO Likes (group_id, liked_by, liked)
                    VALUES (:group_id, :liked_by, :liked)
                """, group_id=group_id, liked_by=liked_by, liked=liked)
                print(2)
                return "liked"
            except Exception as e:
                print(e)
                raise ValueError("Failed to like member") from e

    @staticmethod
    def leave_group(group_id, user_id):
        try:
            rows_deleted = app.db.execute("""
                DELETE FROM MemberInGroup
                WHERE group_id = :group_id AND user_id = :user_id
            """, group_id=group_id, user_id=user_id)
            app.db.execute("""
            DELETE FROM MemberInGroup
            WHERE group_id = :group_id AND liked_by = :user_id
            """, group_id=group_id, user_id=user_id)

            return rows_deleted > 0  # Return True if a row was deleted
        except Exception as e:
            print(str(e))

    @staticmethod
    def generate_matches(group_id):
            return app.db.execute("""
        SELECT u1.name AS liker_name, u2.name AS liked_name
        FROM Likes l1
        JOIN Likes l2 ON l1.liked_by = l2.liked AND l1.liked = l2.liked_by AND l1.group_id = l2.group_id
        JOIN Users u1 ON l1.liked_by = u1.id
        JOIN Users u2 ON l1.liked = u2.id
        WHERE l1.group_id = :group_id
    """, group_id=group_id)
