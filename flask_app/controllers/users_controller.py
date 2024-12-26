from flask_app import app
from flask import render_template, redirect, request, session, flash, url_for
import os
from werkzeug.utils import secure_filename
# import the class from friend.py
from flask_app.models.users_model import User
from flask_app.models.books_model import Book
from flask_app.models.reviews_model import Review
from flask_app.models.authors_model import Author
from flask_app.models.recommendations_model import BookRecommendation
from flask_bcrypt import Bcrypt # GPT Bcrypt
from functools import wraps # wraps stuff
bcrypt = Bcrypt(app)
# from flask_app.models.authors_model import Author
# app = Flask(__name__)

# Configure upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'profile_photos')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
def admin():
    if session.get('role') != 'admin':
        flash('You are not authorized to view this page', 'error')
        return redirect('/')
        
    users = User.get_all_users_with_reviews()
    books = Book.get_all_books()
    reviews = Review.get_all_reviews()
    authors = Author.get_all_authors()
    
    return render_template('admin_dashboard.html', 
                         users=users,
                         books=books,
                         reviews=reviews,
                         authors=authors)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.get_user_by_email(email)
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(f'/user/profile/{user.id}')
        else:
            flash('Invalid email or password', 'error')
            return redirect('/login')
    return render_template('login.html')

@app.route("/login_user", methods=['POST'])
def login_user():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        flash('Please provide both email and password', 'error')
        return redirect('/login')
    
    user = User.get_user_by_email({'email': email})
    
    if user and bcrypt.check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['role'] = user.role
        return redirect(f'/user/profile/{user.id}')
    else:
        flash('Invalid email or password', 'error')
        return redirect('/login')

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
        # Validation errors are already flashed in the validate_user method
        return redirect('/make_an_account')

    # Check if email already exists
    if User.get_user_by_email(request.form['email']):
        flash('Email already exists', 'error')
        return redirect('/make_an_account')

    # Create new user if validation passes
    pw_hash = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
    data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "password": pw_hash,
        "email": request.form["email"],
        "role": request.form.get("role", "user")  # Default to 'user' if not specified
    }
    User.create_user(data)
    flash('Registration successful! Please log in.', 'success')
    return redirect('/login')

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
@login_required
def delete_user(user_id):
    if session['user_id'] != user_id and session['role'] != 'admin':
        flash("You are not authorized to delete this account", "error")
        return redirect('/')
        
    # Get user info before deletion to handle profile photo
    user = User.get_user_by_id(user_id)
    if user and user.profile_photo != 'default.jpg':
        photo_path = os.path.join(UPLOAD_FOLDER, user.profile_photo)
        if os.path.exists(photo_path):
            os.remove(photo_path)
    
    # Delete the user and their data
    if User.delete_user(user_id):
        flash("Account successfully deleted", "success")
    else:
        flash("Error deleting account. Please try again.", "error")
        return redirect(f'/user/profile/{user_id}')
        
    return redirect('/logout')

@app.route('/user/profile/<int:user_id>')
def user_profile(user_id):
    user = User.get_user_with_reviews(user_id)
    if not user:
        flash("User not found", "error")
        return redirect('/')
    return render_template('user_profile.html', user=user)

@app.route('/user/upload_photo', methods=['POST'])
@login_required
def upload_photo():
    if 'photo' not in request.files:
        flash('No file selected', 'error')
        return redirect(request.referrer)
        
    file = request.files['photo']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(request.referrer)
        
    if file and allowed_file(file.filename):
        # Create a unique filename
        filename = secure_filename(f"user_{session['user_id']}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Delete old photo if it exists and isn't the default
        user = User.get_user_by_id(session['user_id'])
        if user.profile_photo != 'default.jpg':
            old_photo_path = os.path.join(UPLOAD_FOLDER, user.profile_photo)
            if os.path.exists(old_photo_path):
                os.remove(old_photo_path)
        
        # Save new photo
        file.save(file_path)
        User.update_profile_photo(session['user_id'], filename)
        flash('Profile photo updated successfully!', 'success')
    else:
        flash('Invalid file type. Please use PNG, JPG, JPEG, or GIF', 'error')
    
    return redirect(request.referrer)

@app.route('/profile')
@login_required
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.get_user_by_id(session['user_id'])
    recommendations = BookRecommendation.get_user_recommendations(session['user_id'])
    return render_template('user_profile.html', user=user, recommendations=recommendations)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect('/')