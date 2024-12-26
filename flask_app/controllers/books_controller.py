from flask import render_template, redirect, request, flash, session, url_for
from flask_app import app
from flask_app.models.users_model import User
from flask_app.models.authors_model import Author
from flask_app.models.books_model import Book
from flask_app.models.publishers_model import Publisher
from flask_app.models.genres_model import Genre
from flask_app.models.reviews_model import Review
from flask_app.models.review_comments_model import ReviewComment
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
@app.route('/books_with_multiple_authors/<int:min_authors>')
@login_required # login
def books_by_author_count(min_authors=2):
    books = Book.get_books_by_author_count(min_authors)
    if not books:
        flash(f"No books found with {min_authors} or more authors.", "info")
        return redirect('/books')
    return render_template("books_w_mult_authors.html", all_books=books, min_authors=min_authors)

@app.route('/book/<int:book_id>')
@login_required # login
def book_with_authors(book_id):
    book = Book.get_book_with_reviews(book_id)  # Updated to include reviews
    if not book:
        flash("No book found with this ID.", "error")
        return redirect('/books')
    all_users = User.get_all_users()  # Get all users for the recommendation dropdown
    return render_template("book_w_authors.html", book=book, all_users=all_users)

@app.route('/book/<int:book_id>/review', methods=['POST'])
@login_required
def add_review(book_id):
    if not 'user_id' in session:
        return redirect('/login')
    
    if not 1 <= int(request.form['stars']) <= 5:
        flash("Rating must be between 1 and 5", "error")
        return redirect(f'/book/{book_id}')
    
    data = {
        'comment': request.form['comment'],
        'stars': request.form['stars'],
        'user_id': session['user_id'],
        'book_id': book_id
    }
    
    Review.create_review(data)
    flash("Review added successfully!", "success")
    return redirect(f'/book/{book_id}')

@app.route('/review/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    if not 'user_id' in session:
        return redirect('/login')
    
    book_id = request.form['book_id']
    Review.delete_review(review_id, session['user_id'])
    flash("Review deleted successfully!", "success")
    return redirect(f'/book/{book_id}')

@app.route('/author/<int:author_id>/books')
def books_by_author(author_id):
    author = Author.get_author_by_id(author_id)
    if not author:
        flash("Author not found", "error")
        return redirect('/books')
        
    books = Book.get_books_by_author(author_id)
    return render_template('books_written_by_this_author.html', 
                         books=books, 
                         author=author)

@app.route('/authors/<int:author_id>/books')
@login_required # login
def books_written_by_this_author(author_id):
    if not session.get('user_id'):
        flash('You must be logged in to view this page', 'danger')
        return redirect('/login')
    data = {
        'id': author_id
    }
    books_shown = Book.get_books_by_author_id(data)
    return render_template('books_written_by_this_author.html', books_shown=books_shown)

@app.route('/books')
@login_required # login
def book_list():
    books = Book.get_all_books()
    return render_template('book_list.html', all_books=books)

# Route to add a new book
@app.route('/books/add', methods=['GET', 'POST'])
@login_required # login
def add_book():
    if request.method == 'POST':
        # Validate the form data
        if not request.form.getlist("author_ids[]"):
            flash("Please select at least one author", "error")
            return redirect('/books/add')
            
        data = {
            "title": request.form["title"],
            "description": request.form["description"],
            "page_count": request.form["page_count"],
            "genre_id": request.form["genre_id"],
            "publisher_id": request.form["publisher_id"],
            "author_ids": request.form.getlist("author_ids[]")
        }
        
        result = Book.create_book(data)
        if result:
            flash("Book added successfully!", "success")
            return redirect('/books')
        else:
            flash("Error adding book. Please try again.", "error")
            return redirect('/books/add')
            
    # GET request - show the form
    authors = Author.get_all_authors()
    publishers = Publisher.get_all_publishers()
    genres = Genre.get_all_genres()
    return render_template('add_book.html', 
                         authors_for_book=authors, 
                         publishers_of_books=publishers, 
                         list_of_genres=genres)

# Route to delete a book
@app.route('/book/<int:book_id>/delete', methods=['GET', 'POST'])
@login_required # login
def delete_this_book(book_id):
    if request.method == 'POST':
        # result = Book.delete_book(book_id)
        if result:
            flash('Book deleted successfully!', 'success')
        else:
            flash('Failed to delete book. Please try again.', 'danger')
    result = Book.delete_book(book_id)
    return redirect('/books')

@app.route('/books/<int:book_id>/edit')
@login_required
def edit_book(book_id):
    book = Book.get_book_with_reviews(book_id)  # This method should already load the authors
    if not book:
        flash("Book not found", "error")
        return redirect('/books')
        
    authors = Author.get_all_authors()
    publishers = Publisher.get_all_publishers()
    genres = Genre.get_all_genres()
    
    return render_template('edit_book.html', 
                         book=book,
                         all_authors=authors,
                         publishers=publishers,
                         genres=genres)

@app.route('/book/<int:book_id>/update', methods=['GET', 'POST'])
@login_required # login
def update_book(book_id):
    if request.method == 'POST':
        # Validate that at least one author is selected
        if not request.form.getlist("author_ids[]"):
            flash("Please select at least one author", "error")
            return redirect(f'/book/{book_id}/update')
            
        data = {
            "id": book_id,
            "title": request.form['title'],
            "description": request.form['description'],
            "page_count": request.form['page_count'],
            "genre_id": request.form['genre_id'],
            "publisher_id": request.form['publisher_id'],
            "author_ids": request.form.getlist("author_ids[]")
        }
        
        result = Book.update_book(data)
        if result:
            flash("Book updated successfully!", "success")
            return redirect('/books')
        else:
            flash("Error updating book. Please try again.", "error")
            return redirect(f'/books/{book_id}/edit')
            
    # GET request - show the form with current data
    book = Book.get_book_by_id(book_id)
    if not book:
        flash("Book not found", "error")
        return redirect('/books')
        
    authors = Author.get_all_authors()
    publishers = Publisher.get_all_publishers()
    genres = Genre.get_all_genres()
    return render_template('edit_book.html', 
                         book=book,
                         authors=authors,
                         publishers=publishers,
                         genres=genres)

@app.route('/review/<int:review_id>/comment', methods=['POST'])
@login_required
def add_review_comment(review_id):
    if not 'user_id' in session:
        return redirect('/login')
    
    data = {
        'comment': request.form['comment'],
        'user_id': session['user_id'],
        'review_id': review_id
    }
    
    ReviewComment.create_comment(data)
    flash("Comment added successfully!", "success")
    return redirect(request.referrer)

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_review_comment(comment_id):
    if not 'user_id' in session:
        return redirect('/login')
    
    ReviewComment.delete_comment(comment_id, session['user_id'])
    flash("Comment deleted successfully!", "success")
    return redirect(request.referrer)
