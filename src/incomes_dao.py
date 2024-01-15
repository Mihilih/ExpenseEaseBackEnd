"""
DAO (Data Access Object) file

Helper file containing functions for accessing data in our database
"""

from db import db, Income, User, Category

def get_all():
    """
    Returns all incomes in the database
    """
    return Income.query.all()

def create_income(user, name, description, category, amount, date):
    """
    Creates an Income object in the database

    Returns if creation was successful, and the Income object
    """
    possible_user = User.query.filter(User.id==user).first()
    print (user)
    print (possible_user)
    if possible_user is None:
        print("NO user")
        return False, None
    print (user)
    possible_category= Category.query.filter(Category.id==category).first()
    if possible_category is None:
        print("NO category")
        return False, None
        
    income = Income(name=name, description=description, amount=amount, user=user, category=category, date=date)
    db.session.add(income)
    possible_category.incomes.append(income)
    possible_user.incomes.append(income)
    db.session.commit()
    return True, income

def get_income_by_id(id):
    """
    Returns an income object from the database given an update token
    """
    possible_income = Income.query.filter(Income.id==id).first()
    if possible_income is None:
        
        return False, None
    return True, possible_income

def delete_income_by_id(id):
    """
    Deletes an income object from the database given an update token
    """
    possible_income = Income.query.filter(Income.id==id).first()
    if possible_income is None:
        print("NO income")
        return False, None
    db.session.delete(possible_income)
    db.session.commit()
    return True, possible_income

def update_income_by_id(id, name, description, category, amount,date):
    """
    Deletes an income object from the database given an update token
    """
    possible_income = Income.query.filter(Income.id==id).first()
    if possible_income is None:
        print("NO income")
        return False, None
    possible_income.name=name
    possible_income.description=description
    possible_income.category=category
    possible_income.amount=amount
    possible_income.date=date
    db.session.commit()
    return True, possible_income