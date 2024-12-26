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
        self.profile_photo = data.get('profile_photo', 'default.jpg')
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
        try:
            # First delete all reviews by this user
            delete_reviews_query = "DELETE FROM reviews WHERE user_id = %(id)s;"
            connect_to_mysql(cls.DB).query_db(delete_reviews_query, {'id': user_id})
            
            # Then delete the user
            delete_user_query = "DELETE FROM users WHERE id = %(id)s;"
            connect_to_mysql(cls.DB).query_db(delete_user_query, {'id': user_id})
            
            return True
        except Exception as e:
            print(f"Error deleting user: {str(e)}")
            return False
    
    @classmethod
    def from_review(cls, data):
        """Create a User object from review data (without password)"""
        data['password'] = None  # Add a dummy password
        data['role'] = data.get('role', 'user')  # Default role to 'user' if not provided
        return cls(data)
    
    @classmethod
    def get_user_with_reviews(cls, user_id):
        """Get a user with all their reviews and the associated books"""
        query = """
            SELECT users.*, reviews.id as review_id, reviews.comment, reviews.stars,
                reviews.created_at as review_created_at, reviews.updated_at as review_updated_at,
                books.id as book_id, books.title as book_title
            FROM users
            LEFT JOIN reviews ON users.id = reviews.user_id
            LEFT JOIN books ON reviews.book_id = books.id
            WHERE users.id = %(id)s;
        """
        results = connect_to_mysql(cls.DB).query_db(query, {'id': user_id})
        
        if not results:
            return None
            
        # Create the user object
        user = cls(results[0])
        user.reviews = []
        
        # Add each review
        for row in results:
            if row['review_id']:  # If there's a review
                review = {
                    'id': row['review_id'],
                    'comment': row['comment'],
                    'stars': row['stars'],
                    'created_at': row['review_created_at'],
                    'updated_at': row['review_updated_at'],
                    'book': {
                        'id': row['book_id'],
                        'title': row['book_title']
                    }
                }
                user.reviews.append(review)
                
        return user
    
    @classmethod
    def get_all_users_with_reviews(cls):
        query = """
            SELECT users.*, COUNT(reviews.id) as review_count
            FROM users
            LEFT JOIN reviews ON users.id = reviews.user_id
            GROUP BY users.id;
        """
        results = connect_to_mysql(cls.DB).query_db(query)
        users = []
        for result in results:
            user = cls(result)
            user.reviews = []  # Initialize empty reviews list
            users.append(user)
        return users
    
    @classmethod
    def update_profile_photo(cls, user_id, photo_filename):
        query = "UPDATE users SET profile_photo = %(photo)s WHERE id = %(id)s;"
        data = {
            'id': user_id,
            'photo': photo_filename
        }
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