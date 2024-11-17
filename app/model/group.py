from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app as app
from ..model.user import User
class Group:

    def __init__(self, id, description, name, owner_id):
        self.id = id
        self.name = name
        self.description = description
        self.owner_id = owner_id
        self._owner=None

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
                INSERT INTO Groups(name, description, password, owner)
                VALUES(:name, :description, :password, :owner) RETURNING id
                """,
                name=name, description = description, password=generate_password_hash(password), owner=owner)
            return rows[0][0]
        except Exception as e:
            # likely name already in use
            print(f"Group Creation error: {str(e)}")
            return None

    @staticmethod
    def get_all():
        rows = app.db.execute("""
                SELECT id, name, description, owner FROM groups
                """)
        print(rows)
        return [Group(*row) for row in rows] if rows else None

    @staticmethod
    def get(group_id):
        rows = app.db.execute("""
                SELECT id, name, description, owner FROM groups WHERE id = :group_id
                """, group_id=group_id)
        return Group(*rows[0]) if rows else None

    @staticmethod
    def get_members(group_id):
        rows = app.db.execute("""
                SELECT users.id, users.name, users.phone, users.email, users.gender FROM users JOIN memberingroup ON users.id=memberingroup.user_id JOIN groups ON memberingroup.group_id = groups.id WHERE groups.id = :id
                """, id=group_id)
        return [User(*row) for row in rows] if rows else None

    @staticmethod
    def _validate_group_password(id, password):
        rows = app.db.execute("""
            SELECT password
            FROM Groups
            WHERE id = :id
            """,
            id=id)
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
                return False
        except:
            return False

    @staticmethod
    def user_in_group(user_id, group_id):
        rows = app.db.execute("""
            SELECT user_id FROM memberingroup WHERE user_id=:user_id AND group_id=:group_id
            """, user_id = user_id, group_id=group_id)
        return True if rows else False
