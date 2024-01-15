"""
DAO (Data Access Object) file

Helper file containing functions for accessing data in our database
"""

from db import db, Expense, User, Category

def get_all():
    """
    Returns all expenses in the database
    """
    return Expense.query.all()

def create_expense(user, name, description, category, amount, date):
    """
    Creates an Expense object in the database

    Returns if creation was successful, and the Expense object
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
        
    expense = Expense(name=name, description=description, amount=amount, user=user, category=category, date=date)
    db.session.add(expense)
    possible_category.expenses.append(expense)
    possible_user.expenses.append(expense)
    db.session.commit()
    return True, expense

def get_expense_by_id(id):
    """
    Returns an expense object from the database given an update token
    """
    possible_expense = Expense.query.filter(Expense.id==id).first()
    if possible_expense is None:
        
        return False, None
    return True, possible_expense

def delete_expense_by_id(id):
    """
    Deletes an expense object from the database given an update token
    """
    possible_expense = Expense.query.filter(Expense.id==id).first()
    if possible_expense is None:
        print("NO expense")
        return False, None
    db.session.delete(possible_expense)
    db.session.commit()
    return True, possible_expense

def update_expense_by_id(id, name, description, category, amount, date):
    """
    Deletes an expense object from the database given an update token
    """
    possible_expense = Expense.query.filter(Expense.id==id).first()
    if possible_expense is None:
        print("NO expense")
        return False, None
    possible_expense.name=name
    possible_expense.description=description
    possible_expense.category=category
    possible_expense.amount=amount
    possible_expense.date=date
    db.session.commit()
    return True, possible_expense