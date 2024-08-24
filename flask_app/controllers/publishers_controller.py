from flask_app import app
from flask_app.config.mysqlconnection import connect_to_mysql
from flask import render_template, redirect, request, session, flash, url_for
from flask_app.models.publishers_model import Publisher
from flask_app.models.authors_model import Author
from functools import wraps # wraps stuff

# decorator v
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
# decorator ^

@app.route('/publishers')
@login_required # login
def publishers_view():
    publishers = Publisher.get_all_publishers()
    return render_template("publishers.html", all_publishers=publishers)

@app.route('/publishers/<int:id>')
@login_required # login
def publisher_detail(id):
    data = {"id": id}
    publisher_listed = Publisher.get_publisher_with_authors(data)
    print(data)
    return render_template("publisher_detail.html", publisher=publisher_listed)

@app.route('/publishers/new')
@login_required # login
def new_publisher():
    authors = Author.get_all_authors() # may need to move
    return render_template("new_publisher.html", list_of_authors = authors)

@app.route('/publishers/create', methods=['POST'])
@login_required # login
def create_publisher():
    if not Publisher.validate_publisher(request.form):
        return redirect('/publishers/new')
    data = {
        "name": request.form["name"],
        "address": request.form["address"],
        "city": request.form["city"],
        "state": request.form["state"],
        "author_id": request.form["author_id"]
    }
    Publisher.create_publisher(data)
    return redirect('/publishers')

@app.route('/publisher/<int:publisher_id>/update', methods=['GET', 'POST'])
@login_required # login
def update_publisher(publisher_id):
    if request.method == 'POST':
        data = {
            "id": publisher_id,
            "name": request.form['name'],
            "address": request.form['address'],
            "city": request.form['city'],
            "state": request.form['state']
        }
        result = Publisher.update_publisher(data)
        if result:
            flash('Publisher updated successfully!', 'success')
            return redirect(f'/book/{publisher_id}')
        else:
            flash('Failed to update publisher. Please try again.', 'danger')
    # Fetch the book data to pre-populate the form
    publisher = Publisher.get_publisher_by_id(publisher_id)
    return render_template('update_publisher.html', publisher=publisher)

# @app.route('/publisher/<int:publisher_id>/delete', methods=['GET', 'POST'])
# @login_required # login
# def delete_this_publisher(publisher_id):
#     if request.method == 'POST':
#         # result = Book.delete_book(book_id)
#         if result:
#             flash('publisher deleted successfully!', 'success')
#         else:
#             flash('Failed to delete publisher. Please try again.', 'danger')
#     result = Publisher.delete_publisher(publisher_id)
#     return redirect('/publishers')

@app.route('/publisher/<int:publisher_id>/delete', methods=['POST'])
@login_required  # login
def delete_this_publisher(publisher_id):
    try:
        # First, delete all entries in author_publishers that reference this publisher
        query = "DELETE FROM author_publishers WHERE publishers_id = %(id)s;"
        data = {"id": publisher_id}
        connect_to_mysql(Publisher.DB).query_db(query, data)

        # Now, delete the publisher itself
        Publisher.delete_publisher(publisher_id)
        flash('Publisher deleted successfully!', 'success')
    except Exception as e:
        flash(f'Failed to delete publisher. Error: {str(e)}', 'danger')
    return redirect('/publishers')
