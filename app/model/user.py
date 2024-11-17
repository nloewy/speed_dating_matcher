from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login

class User(UserMixin):
    def __init__(self, id, name, phone, email, gender):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.gender = gender

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
            SELECT password, id, name, phone, email, gender
            FROM Users
            WHERE email = :email
            """,
            email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):  # incorrect password
            return None
        else:
            return User(*rows[0][1:])

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
            SELECT email
            FROM Users
            WHERE email = :email
            """,
            email=email)
        return len(rows) > 0

    @staticmethod
    def register(name, phone, email, gender, password):
        try:
            rows = app.db.execute("""
                INSERT INTO Users(name, phone, email, gender, password)
                VALUES(:name, :phone, :email, :gender, :password) RETURNING id
                """,
                name=name, phone=phone, email=email, gender=gender,
                password=generate_password_hash(password))
            return rows[0][0]
        except Exception as e:
            # likely email already in use
            print(f"Registration error: {str(e)}")
            return None

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
            SELECT id, name, phone, email, gender
            FROM Users
            WHERE id = :id
            """,
            id=id)
        return User(*rows[0]) if rows else None

    @staticmethod
    def get_all():
        rows = app.db.execute("""
            SELECT id, name, phone, email, gender
            FROM Users
            """)
        return [User(*row) for row in rows] if rows else None


