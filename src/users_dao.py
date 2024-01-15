"""
DAO (Data Access Object) file

Helper file containing functions for accessing data in our database
"""

from db import db, User

def get_all():
    """
    Returns all users in the database
    """
    return User.query.all()

def verify_credentials(email, password):
    """
    Returns true if the credentials match, otherwise returns false
    """
    possible_user=get_user_by_email(email)
    if possible_user is None:
        return False, None
    return possible_user.verify_password(password), possible_user


def get_user_by_session_token(session_token):
    """
    Returns a user object from the database given a session token
    """
    return User.query.filter(User.session_token == session_token).first()


def get_user_by_update_token(update_token):
    """
    Returns a user object from the database given an update token
    """
    return User.query.filter(User.update_token == update_token).first()


def get_user_by_email(email):
    """
    Returns a user object from the database given an email
    """
    return User.query.filter(User.email == email).first()

def create_user(first_name, last_name, username, email, password, curr_amt):
    """
    Creates a User object in the database

    Returns if creation was successful, and the User object
    """
    try:
        possible_user=get_user_by_email(email)
        if possible_user is not None:
            return False, possible_user
        user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, curr_amt=curr_amt)
        db.session.add(user)
        db.session.commit()
        return True, user
    except Exception as e:
        print(e)
        return False, None

def delete_user(session_token):
    """
    Deletes a User object in the database

    Returns if creation was successful, and the User object
    """
    user = User.query.filter_by(session_token=session_token).first()
    if user is None:
        return False, None
    db.session.delete(user)
    db.session.commit()
    return True, user


def update_user(session_token, id, first_name, last_name, username, email, curr_amt):
    """
    Updates the data of a User object in the database

    Returns is update was successful, ans the User object
    """
    possible_user1=User.query.filter_by(id=id).first()
    if possible_user1 is None:
        return False, None
    possible_user2=User.query.filter_by(session_token=session_token).first()
    if possible_user2 is None:
        return False, None
    if possible_user2!=possible_user1:
        return False, None
    possible_user1.first_name = first_name
    possible_user1.last_name = last_name
    possible_user1.username = username
    possible_user1.email = email
    possible_user1.curr_amt = curr_amt
    db.session.commit()
    return True, possible_user1