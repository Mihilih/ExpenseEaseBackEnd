from flask_sqlalchemy import SQLAlchemy
import bcrypt
import datetime
import hashlib
import os

db = SQLAlchemy()

user_category_table=db.Table(
    "user_category",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("category_id", db.Integer, db.ForeignKey("category.id")),
    db.Column("budget", db.Integer)
)

class User(db.Model):
    """
    User Model
    """
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password_digest = db.Column(db.String, nullable=False)
    curr_amt = db.Column(db.Integer, nullable=False)

    categories = db.relationship("Category", secondary=user_category_table, back_populates="users")
    expenses = db.relationship("Expense", cascade="delete")
    incomes = db.relationship("Income", cascade="delete")

    
    # Session information
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)


    def __init__(self, **kwargs):
        """
        Initializes User object
        """
        self.first_name = kwargs.get("first_name", "")
        self.last_name = kwargs.get("last_name", "")
        self.email = kwargs.get("email", "")
        self.username = kwargs.get("username", "")
        self.password_digest = bcrypt.hashpw(kwargs.get("password").encode("utf8"), bcrypt.gensalt(rounds=13))
        self.curr_amt = kwargs.get("curr_amt", "")
        self.renew_session()

    def _urlsafe_base_64(self):
        """
        Randomly generates hashed tokens (used for session/update tokens)
        """
        return hashlib.sha1(os.urandom(64)).hexdigest()

    def renew_session(self):
        """
        Renews the sessions, i.e.
        1. Creates a new session token
        2. Sets the expiration time of the session to be a day from now
        3. Creates a new update token
        """
        self.session_token = self._urlsafe_base_64()
        self.session_expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        self.update_token = self._urlsafe_base_64()

    def verify_password(self, password):
        """
        Verifies the password of a user
        """
        return bcrypt.checkpw(password.encode("utf8"), self.password_digest)

    def verify_session_token(self, session_token):
        """
        Verifies the session token of a user
        """
        return session_token == self.session_token and datetime.datetime.now() < self.session_expiration

    def verify_update_token(self, update_token):
        """
        Verifies the update token of a user
        """
        return update_token == self.update_token

    def serialize(self):
        """
        Serializes a User object
        """
        return {"id": self.id, "first_name": self.first_name, "last_name": self.last_name,"email": self.email, "username": self.username, "current_balance": self.curr_amt, "categories": [c.simpleSerialize() for c in self.categories], "expenses": [c.serialize() for c in self.expenses], "incomes": [c.serialize() for c in self.incomes]}


class Category(db.Model):
    """
    Category Model
    """
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    
    users = db.relationship("User", secondary=user_category_table, back_populates="categories")
    expenses = db.relationship("Expense", cascade="delete")
    incomes = db.relationship("Income", cascade="delete")

    
    def __init__(self, **kwargs):
        """
        Initializes Category object
        """
        self.name = kwargs.get("name", "")

    def simpleSerialize(self):
        """
        Serializes a Category object
        """
        return {"id": self.id, "name": self.name}

    def serialize(self):
        """
        Serializes a Category object
        """
        return {"id": self.id, "name": self.name, "expenses": [c.serialize() for c in self.expenses], "income": [c.serialize() for c in self.incomes]}


class Expense(db.Model):
    """
    Expense Model
    """
    __tablename__ = "expense"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    category = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    
    def __init__(self, **kwargs):
        """
        Initializes Expense object
        """
        self.name = kwargs.get("name", "")
        self.description = kwargs.get("description", "")
        self.date = kwargs.get("date", "")
        self.amount = kwargs.get("amount", "")
        self.user = kwargs.get("user", "")
        self.category = kwargs.get("category", "")

    def serialize(self):
        """
        Serializes a Expense object
        """
        return {"id": self.id, "name": self.name, "description": self.description, "amount": self.amount, "user": self.user, "category": self.category, "date": str(self.date)}
    
class Income(db.Model):
    """
    Income Model
    """
    __tablename__ = "income"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    user = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    category = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    
    
    def __init__(self, **kwargs):
        """
        Initializes Income object
        """
        self.name = kwargs.get("name", "")
        self.description = kwargs.get("description", "")
        self.date = kwargs.get("date", "")
        self.amount = kwargs.get("amount", "")
        self.user = kwargs.get("user", "")
        self.category = kwargs.get("category", "")

    def serialize(self):
        """
        Serializes a Income object
        """
        return {"id": self.id, "name": self.name, "description": self.description, "amount": self.amount, "user": self.user, "category": self.category, "date": str(self.date)}