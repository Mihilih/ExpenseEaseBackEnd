import json

from db import db, User, Expense, Income, Category
from flask import Flask
from flask import request
import users_dao, categories_dao, expenses_dao, incomes_dao
import os
import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv
import os

load_dotenv()
db_filename = "expense.db"
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
EMAIL_API = os.getenv("EMAIL_API")

db.init_app(app)
with app.app_context():
    db.create_all()


# generalized response formats
def success_response(data, code=200):
    """
    Generalized success response function
    """
    return json.dumps(data), code

def failure_response(message, code=404):
    """
    Generalized failure response function
    """
    return json.dumps({"error": message}), code

def extract_token(request):
    """
    Helper function that extracts the token from the header of a request
    """
    auth_header=request.headers.get("Authorization")
    if auth_header is None:
        return False, failure_response("Missing Authorization header")
    bearer_token = auth_header.replace("Bearer", "").strip()
    if not bearer_token:
        return False, failure_response("Invalid Authorization header")
    print("BEARER "+ bearer_token)
    return True, bearer_token


#User routes
@app.route("/")
def home():
    """
    Endpoint for the homepage
    
    Gets current user information
    """
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    user=users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    user = users_dao.get_user_by_session_token(session_token)
    if user is None:
        return failure_response("User does't exist")
    print("THIS IS MY USER" + str(user))
    return success_response(user.serialize())

@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a new user"
    """
    body = json.loads(request.data)
    first_name=body.get("first_name")
    last_name=body.get("last_name")
    email=body.get("email")
    username=body.get("username")
    password=body.get("password")
    amt = body.get("amt")
    if first_name==None or amt==None or username==None or last_name==None or email==None or password==None:
        return failure_response("Invalid body")
    created, user = users_dao.create_user(first_name, last_name, username, email, password, amt)
    if not created:
        return failure_response("Email already exists")
    return success_response({"session_token": user.session_token, "session_expiration": str(user.session_expiration), "update_token": user.update_token}, 201)

@app.route("/api/login/", methods=["POST"])
def login():
    """
    Endpoint for logging in a user
    """
    body = json.loads(request.data)
    email=body.get("email")
    password=body.get("password")
    if email==None or password==None:
        return failure_response("Invalid body")
    exists, user = users_dao.verify_credentials(email, password)
    if not exists:
        return failure_response("Invalid credentials")
    user.renew_session()
    db.session.commit()
    return success_response({"session_token": user.session_token, "session_expiration": str(user.session_expiration), "update_token": user.update_token})

@app.route("/api/logout/", methods=["POST"])
def logout():
    """
    Endpoint for logging out a user
    """
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    user=users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    user.session_expiration = datetime.datetime.now()
    return success_response("You have been logged out")

@app.route("/api/users/", methods=["DELETE"])
def delete_user():
    """
    Endpoint for deleting a user
    """
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    user=users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    result, user = users_dao.delete_user(session_token)
    if result:
        return success_response(user.serialize())
    return failure_response("User not found")

@app.route("/api/users/<int:id>/", methods=["POST"])
def update_user(id):
    """
    Endpoint for updating user details
    """
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    user=users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    body = json.loads(request.data)
    first_name=body.get("first_name")
    last_name=body.get("last_name")
    email=body.get("email")
    username=body.get("username")
    amt = body.get("amt")
    if first_name==None or amt==None or username==None or last_name==None or email==None:
        return failure_response("Invalid body")
    updated, user = users_dao.update_user(session_token, id, first_name, last_name, username, email, amt)
    if not updated:
        return failure_response("Failed to update user")
    return success_response(user.serialize(), 201)

@app.route("/api/users/")
def get_all_users():
    """
    Endpoint for getting all users
    """
    users = users_dao.get_all()
    lst = [user.serialize() for user in users]
    return success_response(lst)

#category routes
@app.route("/api/categories/", methods=["POST"])
def create_category():
    """
    Endpoint for creating a new category"
    """
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    body = json.loads(request.data)
    name=body.get("name")
    isexpense=body.get("isexpense")
    if name==None or isexpense==None:
        return failure_response("Invalid body")
    created, category = categories_dao.create_category(name, isexpense)
    if not created:
        return failure_response("Category already exists")
    return success_response(category.serialize(), 201)

@app.route("/api/categories/")
def get_all_categories():
    """
    Endpoint for getting all categories
    """
    categories = categories_dao.get_all()
    lst = [category.serialize() for category in categories]
    return success_response(lst)

#expense routes
@app.route("/api/expense/", methods=["POST"])
def create_expense():
    """
    Endpoint for creating a new expense"
    """
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    user1 = users_dao.get_user_by_session_token(session_token)
    if not user1 or not user1.verify_session_token(session_token):
        return failure_response("Invalid session token")
    body = json.loads(request.data)
    name=body.get("name")
    user=body.get("user")
    description=body.get("description")
    category=body.get("category")
    amount=body.get("amount")
    date = datetime.date.today()
    if name==None or user==None or description==None or category==None or amount==None:
        return failure_response("Invalid body")
    created, expense = expenses_dao.create_expense(user, name, description, category, amount, date)
    if not created:
        return failure_response("User does not exist")
    user1.curr_amt = user1.curr_amt-amount
    db.session.commit()
    return success_response(expense.serialize(), 201)

@app.route("/api/expense/<int:id>/", methods=["DELETE"])
def delete_expense(id):
    """
    Endpoint for deleting an expenese
    """
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    user1 = users_dao.get_user_by_session_token(session_token)
    if not user1 or not user1.verify_session_token(session_token):
        return failure_response("Invalid session token")
    user=users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    result, expense = expenses_dao.delete_expense_by_id(id)
    if result:
        user.curr_amt = user.curr_amt+expense.amount
        db.session.commit()
        return success_response(expense.serialize())
    return failure_response("Expense not found")

@app.route("/api/expense/<int:id>/")
def get_expense(id):
    """
    Endpoint for deleting an expenese
    """
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    user=users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    
    result, expense = expenses_dao.get_expense_by_id(id)
    if result:
        user.curr_amt = user.curr_amt+expense.amount
        db.session.commit()
        return success_response(expense.serialize())
    
    return failure_response("Expense not found")

@app.route("/api/expense/<int:id>/", methods=["POST"])
def update_expense(id):
    """
    Endpoint for deleting an expenese
    """
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    user1 = users_dao.get_user_by_session_token(session_token)
    if not user1 or not user1.verify_session_token(session_token):
        return failure_response("Invalid session token")
    body = json.loads(request.data)
    name=body.get("name")
    description=body.get("description")
    category=body.get("category")
    amount=body.get("amount")
    
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    user=users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    success, prev_expense = expenses_dao.get_expense_by_id(id)
    print("PREV" + repr(prev_expense))
    prev_amt=prev_expense.amount
    date = prev_expense.date
    result, expense = expenses_dao.update_expense_by_id(id, name, description, category, amount, date)
    if result:
        user.curr_amt = user.curr_amt-amount+prev_amt
        db.session.commit()
        return success_response(expense.serialize())
    user.curr_amt = user.curr_amt-amount+prev_amt
    db.session.commit()
    return failure_response("Expense not found")

@app.route("/api/expenses/")
def get_all_expenses():
    """
    Endpoint for getting all expenses
    """
    expenses = expenses_dao.get_all()
    lst = [expense.serialize() for expense in expenses]
    return success_response(lst)

#income routes
@app.route("/api/income/", methods=["POST"])
def create_income():
    """
    Endpoint for creating a new income"
    """
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    user1 = users_dao.get_user_by_session_token(session_token)
    if not user1 or not user1.verify_session_token(session_token):
        return failure_response("Invalid session token")
    print("SESSION "+ session_token)
    body = json.loads(request.data)
    name=body.get("name")
    user=body.get("user")
    description=body.get("description")
    category=body.get("category")
    amount=body.get("amount")
    date = datetime.date.today()
    if name==None or user==None or description==None or category==None or amount==None:
        return failure_response("Invalid body")
    created, income = incomes_dao.create_income(user, name, description, category, amount, date)
    if not created:
        return failure_response("User does not exist")
    print(session_token)
    user2 = users_dao.get_user_by_session_token(session_token=session_token)
    print("USER" + str(user2))
    user2.curr_amt = user2.curr_amt+amount
    db.session.commit()
    return success_response(income.serialize(), 201)

@app.route("/api/income/<int:id>/", methods=["DELETE"])
def delete_income(id):
    """
    Endpoint for deleting an expenese
    """
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    user1 = users_dao.get_user_by_session_token(session_token)
    if not user1 or not user1.verify_session_token(session_token):
        return failure_response("Invalid session token")
    user=users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    result, income = incomes_dao.delete_income_by_id(id)
    if result:
        user.curr_amt = user.curr_amt-income.amount
        db.session.commit()
        return success_response(income.serialize())
    
    return failure_response("Income not found")

@app.route("/api/income/<int:id>/")
def get_income(id):
    """
    Endpoint for deleting an expenese
    """
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    user1 = users_dao.get_user_by_session_token(session_token)
    if not user1 or not user1.verify_session_token(session_token):
        return failure_response("Invalid session token")
    user=users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    
    result, income = incomes_dao.get_income_by_id(id)
    if result:
        return success_response(income.serialize())
    return failure_response("Income not found")

@app.route("/api/income/<int:id>/", methods=["POST"])
def update_income(id):
    """
    Endpoint for deleting an expenese
    """
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    user1 = users_dao.get_user_by_session_token(session_token)
    if not user1 or not user1.verify_session_token(session_token):
        return failure_response("Invalid session token")
    body = json.loads(request.data)
    name=body.get("name")
    description=body.get("description")
    category=body.get("category")
    amount=body.get("amount")
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    user=users_dao.get_user_by_session_token(session_token)
    success, prev_income = incomes_dao.get_income_by_id(id)
    prev_amt=prev_income.amount
    date = prev_income.date
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    result, income = incomes_dao.update_income_by_id(id, name, description, category, amount, date)
    if result:
        user.curr_amt = user.curr_amt+amount-prev_amt
        db.session.commit() 
        return success_response(income.serialize())
    
    return failure_response("Income not found")

@app.route("/api/incomes/")
def get_all_incomes():
    """
    Endpoint for getting all expenses
    """
    incomes = incomes_dao.get_all()
    lst = [income.serialize() for income in incomes]
    return success_response(lst)

@app.route("/api/email/")
def email_report():
    """
    Endpoint for sending an email report
    """
    success, session_token = extract_token(request)
    if not success:
        return failure_response(session_token)
    user=users_dao.get_user_by_session_token(session_token)
    print(user.email)
    expense = 0
    for ex in user.expenses:
        expense = expense+ex.amount

    income = 0
    for inc in user.incomes:
        income = income+inc.amount
    print(EMAIL_API)
    message = Mail(Email("noreply.expenseease@gmail.com"),
                   To(user.email),
                   "Your spending report",
                   Content("text/plain", "Your expenses so far is $" + str(expense) + " and your income so far is $" + str(income)))
    try:
        print(EMAIL_API)
        sg = SendGridAPIClient(EMAIL_API)
        response = sg.client.mail.send.post(message.get())
        print(response.status_code)
        return success_response("sent email successfully")
    except Exception as e:
        print(e)
        return failure_response("internal error")

    


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
