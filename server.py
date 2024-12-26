from flask import Flask

from flask_app import app
from flask_app.controllers import users_controller, authors_controller, books_controller, publishers_controller, recommendations_controller
# app = Flask(__name__)
         
if __name__ == "__main__":
    app.run(debug=True, port=5000)

