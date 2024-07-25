from flask_app.config.mysqlconnection import connect_to_mysql
# import the function that will return an instance of a connection
from flask import flash
import re


# model the class after the user table from our database

# password_pattern = re.compile(
#     r"""
#     ^                # start of string
#     (?=.*[A-Z])      # at least one uppercase letter
#     (?=.*[a-z])      # at least one lowercase letter
#     (?=.*\d)         # at least one digit
#     (?=.*[@$!%*?&])  # at least one special character
#     [A-Za-z\d@$!%*?&] # allowed characters
#     {8,}             # at least 8 characters long
#     $                # end of string
#     """, re.VERBOSE)
# password_pattern = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+[@$!%*?&]+$')

class User:
    DB = 'mydb'
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.role = data['role']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
    # Now we use class methods to query our database

    @classmethod
    def get_user_by_email(cls, email):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        data = {"email": email}
        results = connect_to_mysql(cls.DB).query_db(query, data)
        if results:
            return cls(results[0])
        return None
    
    @classmethod
    def get_all_users(cls):
        query = "SELECT * FROM users;"
        # make sure to call the connect_to_mysql function with the schema you are targeting.
        results = connect_to_mysql(cls.DB).query_db(query)
        # Create an empty list to append our instances of friends
        users = []
        # Iterate over the db results and create instances of friends with cls.
        for user in results:
            users.append(cls(user))
        return users
    
    @classmethod
    def create_user(cls, data):
        query = "INSERT INTO users (first_name, last_name, email, password, role, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, %(role)s, NOW(), NOW());"
        # data is a dictionary that will be passed into the save method from server.py
        return connect_to_mysql(cls.DB).query_db(query, data)
    
    @classmethod
    def get_user_by_id(cls, user_id):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        data = {"id": user_id}
        results = connect_to_mysql(cls.DB).query_db(query, data)
        return cls(results[0])
    
    @classmethod
    def update(cls,data):
        query = """
                UPDATE users SET first_name=%(first_name)s,last_name=%(last_name)s,
                email=%(email)s, password=%(password)s, role=%(role)s
                WHERE id = %(id)s;
                """
        results = connect_to_mysql(cls.DB).query_db(query,data)
        return results
    
    @classmethod
    def delete_user(cls, user_id):
        query  = "DELETE FROM users WHERE id = %(id)s;"
        data = {"id": user_id}
        return connect_to_mysql(cls.DB).query_db(query, data)
    
    @staticmethod
    def validate_user(user):
        # password_pattern = re.compile(r'^.*(?=.{8,10})(?=.*[a-zA-Z])(?=.*?[A-Z])(?=.*\d)[a-zA-Z0-9!@$%^&*()_+={}?:~\[\]]+$')
        password_pattern = re.compile(
            r"""
            ^                 # start of string
            (?=.*[A-Z])       # at least one uppercase letter
            (?=.*[a-z])       # at least one lowercase letter
            (?=.*\d)          # at least one digit
            (?=.*[@$!%*?&])   # at least one special character
            [A-Za-z\d@$!%*?&] # allowed characters
            {8,}              # at least 8 characters long
            $                 # end of string
            """, re.VERBOSE)
        is_valid = True
        if len(user['first_name']) < 2:
            flash("First name must be at least 2 characters.", "register")
            is_valid = False
        if len(user['last_name']) < 2:
            flash("Last name must be at least 2 characters.", "register")
            is_valid = False
        if len(user['email']) < 5:
            flash("Email must be valid.", "register")
            is_valid = False
        if 'password' in user and len(user['password']) < 8:
            flash("Password must be at least 8 characters.", "register")
            is_valid = False
        if 'password' in user and not password_pattern.match(user['password']):
            flash("password must be at least 8 characters, contain an upper and lowercase char and one symbol and number")
            is_valid = False
        return is_valid