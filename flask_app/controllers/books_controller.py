from flask import render_template, redirect, request, flash, session, url_for
from flask_app import app
from flask_app.models.authors_model import Author
from flask_app.models.books_model import Book
from flask_app.models.publishers_model import Publisher
from flask_app.models.genres_model import Genre
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

@app.route('/books_with_multiple_authors')
@login_required # login
def get_books_that_have_multiple_authors():
    books = Book.get_books_with_multiple_authors()
    if not books:
        return "No books found with multiple authors."
    return render_template("books_w_mult_authors.html", all_books=books)

@app.route('/book/<int:book_id>')
@login_required # login
def book_with_authors(book_id):
    data = {"id": book_id}
    book = Book.get_book_w_author(data)
    if not book:
        return "No book found with this ID."
    return render_template("book_w_authors.html", book=book)

@app.route('/authors/<int:author_id>/books')
@login_required # login
def books_written_by_this_author(author_id):
    data = {"id": author_id}
    books_written = Author.get_author_w_books(data)
    if not books_written or not books_written.books_by_this_author:
        return "No books found for this author."
    return render_template('books_written_by_this_author.html', books_shown=books_written)

@app.route('/books')
@login_required # login
def book_list():
    books = Book.get_all_books()
    return render_template('book_list.html', all_books=books)

# Route to add a new book
@app.route('/books/add', methods=['GET', 'POST'])
@login_required # login
def add_book():
    authors = Author.get_all_authors()
    publishers = Publisher.get_all_publishers()
    genres = Genre.get_all_genres()
    if request.method == 'POST':
        data = {
            "title": request.form['title'],
            "description": request.form['description'],
            "page_count": request.form['page_count'],
            "genre_id": request.form['genre_id'],
            "author_id": request.form['author_id'],
            "publisher_id": request.form['publisher_id']
        }
        result = Book.create_book(data)
        if result:
            flash('Book added successfully!', 'success')
            return redirect('/books')
        else:
            flash('Failed to add book. Please try again.', 'danger')
    return render_template('add_book.html', authors_for_book = authors, publishers_of_books = publishers, list_of_genres = genres)

# Route to delete a book
@app.route('/book/<int:book_id>/delete', methods=['POST'])
@login_required # login
def delete_book(book_id):
    result = Book.delete_book(book_id)
    if result:
        flash('Book deleted successfully!', 'success')
    else:
        flash('Failed to delete book. Please try again.', 'danger')
    return redirect('/books_with_multiple_authors')

# Route to update a book
@app.route('/book/<int:book_id>/update', methods=['GET', 'POST'])
@login_required # login
def update_book(book_id):
    if request.method == 'POST':
        data = {
            "id": book_id,
            "title": request.form['title'],
            "description": request.form['description'],
            "page_count": request.form['page_count']
        }
        result = Book.update(data)
        if result:
            flash('Book updated successfully!', 'success')
            return redirect(f'/book/{book_id}')
        else:
            flash('Failed to update book. Please try again.', 'danger')
    # Fetch the book data to pre-populate the form
    book = Book.get_book_by_id(book_id)
    return render_template('update_book.html', book=book)

