from flask_app import app
from flask import render_template, redirect, request
from flask_app.models.publishers_model import Publisher
from flask_app.models.authors_model import Author

@app.route('/publishers')
def publishers_view():
    publishers = Publisher.get_all_publishers()
    return render_template("publishers.html", all_publishers=publishers)

@app.route('/publishers/<int:id>')
def publisher_detail(id):
    data = {"id": id}
    publisher = Publisher.get_publisher_with_authors(data)
    print(data)
    return render_template("publisher_detail.html", publisher=publisher)

@app.route('/publishers/new')
def new_publisher():
    authors = Author.get_all_authors() # may need to move
    return render_template("new_publisher.html", list_of_authors = authors)

@app.route('/publishers/create', methods=['POST'])
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
