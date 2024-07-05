from flask_app import app
from flask import render_template, redirect, request
from flask_app.models.authors_model import Author
from flask_app.models.books_model import Book
from flask_app.models.publishers_model import Publisher

@app.route('/authors')
def authors_view():
    authors = Author.get_all_authors()
    return render_template("authors.html", all_authors=authors)

@app.route('/authors/new')
def new_author():
    return render_template("new_author.html")

@app.route('/books_written_by_this_author/display/<int:author_id>')
def books_by_author_view(author_id):
    data = {"id": author_id}
    books_written = Author.get_author_w_books(data)
    return render_template('books_written_by_this_author.html', books_shown=books_written)

@app.route('/authors/create', methods=['POST'])
def create_author():
    data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "publisher_id": request.form.get("publisher_id", None)
    }
    Author.create_author(data)
    return redirect('/authors')

@app.route('/authors/<int:id>/edit')
def edit_author(id):
    data = {"id": id}
    author = Author.get_author_by_id(data)
    return render_template("edit_author.html", author=author)

@app.route('/authors/update', methods=['POST'])
def update_author():
    data = {
        "id": request.form["id"],
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"]
    }
    Author.update(data)
    return redirect('/authors')

@app.route('/authors/<int:author_id>/delete')
def delete_author(author_id):
    Author.delete_author({"id": author_id})
    return redirect('/authors')
