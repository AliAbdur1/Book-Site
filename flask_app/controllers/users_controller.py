from flask_app import app
from flask import render_template, redirect, request, session, flash, url_for
# import the class from friend.py
from flask_app.models.users_model import User
from flask_bcrypt import Bcrypt # GPT Bcrypt
from functools import wraps # wraps stuff
bcrypt = Bcrypt(app)
# from flask_app.models.authors_model import Author
# app = Flask(__name__)

# decorator v
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                flash('Please log in to access this page', 'warning')
                return redirect(url_for('login'))
            user = User.get_user_by_id(user_id)
            if user.role != required_role:
                flash('You do not have the necessary permissions to access this page', 'danger')
                return redirect('/')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
# decorator ^

def user_matches_session(user_id):
    return session.get('user_id') == user_id

@app.route("/admin")
@login_required
@role_required('admin')
def admin_dashboard():
    users = User.get_all_users()
    return render_template("admin_dashboard.html", users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.get_user_by_email(email)
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role  # Store role in session
            flash('Login successful', 'success')
            return redirect('/')
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route("/")
@login_required # login
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
    if not User.validate_user(request.form):
        return redirect('/make_an_account')
    # First we make a data dictionary from our request.form coming from our template.
    # The keys in data need to line up exactly with the variables in our query string.
    pw_hash = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
    data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "password": pw_hash,
        "email": request.form["email"],
        "role": request.form["role"]  # Assuming role is provided in the form
    }
    # We pass the data dictionary into the save method from the Friend class.
    User.create_user(data)
    flash('User created successfully', 'success')
    # Don't forget to redirect after saving to the database.
    return redirect('/')

@app.route('/user/show/<int:user_id>')
@login_required # login
def show(user_id):
    if not user_matches_session(user_id):
        flash('You are not authorized to view this page', 'danger')
        return redirect('/')
    # calling the get_one method and supplying it with the id of the user we want to get
    this_user = User.get_user_by_id(user_id)
    return render_template("show_user.html", user = this_user)

@app.route('/user/update/<int:user_id>',methods=['POST'])
@login_required # login
def update_user(user_id):
    if not user_matches_session(user_id) and not session.get('role') == 'admin':
        flash('You are not authorized to view this page', 'danger')
        return redirect('/')
    # Create a data dictionary from request.form and add the user ID
    data = {
        "id": user_id,
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "email": request.form["email"]
        # "password": request.form["password"],
        # "role": request.form["role"]
    }
    if request.form['password']:
        data['password'] = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
    else:
        # Get the current user's password hash from the database
        current_user = User.get_user_by_id(user_id)
        data['password'] = current_user.password
    # Include the role from the form
    data['role'] = request.form['role']
    # Validate user input
    if not User.validate_user(data):
        return redirect(f'/user/show/{user_id}')
    # Update the user in the database
    User.update(data)
    flash('User updated successfully', 'success')
    # make sure whats updated here matches query
    User.update(data)
    return redirect('/')

@app.route('/user/delete/<int:user_id>')
@login_required # login
def delete(user_id):
    if not user_matches_session(user_id):
        flash('You are not authorized to view this page', 'danger')
        return redirect('/')
    User.delete_user(user_id)
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect('/')