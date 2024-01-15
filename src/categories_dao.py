"""
DAO (Data Access Object) file

Helper file containing functions for accessing data in our database
"""

from db import db, Category

def get_all():
    """
    Returns all categories in the database
    """
    return Category.query.all()

def get_category_by_name(name):
    """
    Returns a user object from the database given an email
    """
    return Category.query.filter(Category.name == name).first()

def create_category(name, isexpense):
    """
    Creates a Category object in the database

    Returns if creation was successful, and the User object
    """
    
    possible_category=get_category_by_name(name.capitalize())
    if possible_category is not None:
        return False, possible_category
    category = Category(name=name, isexpense=isexpense)
    db.session.add(category)
    db.session.commit()
    return True, category