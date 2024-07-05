from flask_app import app
from flask import render_template, redirect, request
# import the class from friend.py
from flask_app.models.users_model import User
# from flask_app.models.authors_model import Author
# app = Flask(__name__)

@app.route("/")
def index():
    # call the get all classmethod to get all users
    users = User.get_all_users()
    print(users)
    return render_template("index.html", users=users)

@app.route("/make_an_account")
def make_account_route():
    return render_template("user_form.html")

@app.route('/create_user', methods=["POST"])
def create_user():
    # First we make a data dictionary from our request.form coming from our template.
    # The keys in data need to line up exactly with the variables in our query string.
    data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "password": request.form["password"],
        "email": request.form["email"]
    }
    # We pass the data dictionary into the save method from the Friend class.
    User.create_user(data)
    # Don't forget to redirect after saving to the database.
    return redirect('/')

@app.route('/user/show/<int:user_id>')
def show(user_id):
    # calling the get_one method and supplying it with the id of the friend we want to get
    this_user = User.get_user_by_id(user_id)
    return render_template("show_user.html", user = this_user)

@app.route('/user/update/<int:user_id>',methods=['POST'])
def update_user(user_id):
    # Create a data dictionary from request.form and add the user ID
    data = {
        "id": user_id,
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "email": request.form["email"],
        "password": request.form["password"]
    }
    # make sure whats updated here matches query
    User.update(data)
    return redirect('/')

@app.route('/user/delete/<int:user_id>')
def delete(user_id):
    User.delete_user(user_id)
    return redirect('/')