from flask_app.config.mysqlconnection import connect_to_mysql
from flask_app.models import books_model
from flask_app.models import publishers_model
from flask import flash

class Author:
    DB = 'mydb'
    
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.publisher_id = data.get('publisher_id')
        self.publisher = None
        self.books_by_this_author = []
        
    
    @classmethod
    def get_all_authors(cls):
        query = "SELECT * FROM authors;"
        results = connect_to_mysql(cls.DB).query_db(query)
        authors = []
        for author in results:
            authors.append(cls(author))
        return authors
    
    @classmethod
    def get_author_w_books(cls, data):
        query = """
            SELECT authors.*, 
                   books.id AS book_id, 
                   books.title, 
                   books.description, 
                   books.page_count,
                   books.created_at AS book_created_at, 
                   books.updated_at AS book_updated_at,
                   books.genre_id, 
                   books.publisher_id
            FROM authors
            LEFT JOIN book_authors ON authors.id = book_authors.author_id
            LEFT JOIN books ON books.id = book_authors.book_id
            WHERE authors.id = %(id)s;
        """
        results = connect_to_mysql(cls.DB).query_db(query, data)
        if not results:
            return None
            
        author = cls(results[0])
        author.books_by_this_author = []
        
        for row in results:
            if row['book_id']:
                book_data = {
                    'id': row['book_id'],
                    'title': row['title'],
                    'description': row['description'],
                    'page_count': row['page_count'],
                    'created_at': row['book_created_at'],
                    'updated_at': row['book_updated_at'],
                    'genre_id': row['genre_id'],
                    'publisher_id': row['publisher_id']
                }
                author.books_by_this_author.append(book_data)
                
        return author
    
    @classmethod
    def get_author_with_publisher(cls, data):
        query = """
            SELECT * FROM authors
            LEFT JOIN publishers ON publishers.id = authors.publisher_id
            WHERE authors.id = %(id)s;
        """
        results = connect_to_mysql(cls.DB).query_db(query, data)
        if not results:
            return None
        author = cls(results[0])
        if results[0]["publishers.id"]:
            publisher_data = {
                "id": results[0]["publishers.id"],
                "name": results[0]["publishers.name"],
                "address": results[0]["publishers.address"],
                "city": results[0]["publishers.city"],
                "state": results[0]["publishers.state"],
                "created_at": results[0]["publishers.created_at"],
                "updated_at": results[0]["publishers.updated_at"]
            }
            author.publisher = publishers_model.Publisher(publisher_data)
        return author
    
    @classmethod
    def create_author(cls, data):
        query = "INSERT INTO authors (first_name, last_name, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, NOW(), NOW());"
        return connect_to_mysql(cls.DB).query_db(query, data)
    
    @classmethod
    def get_author_by_id(cls, data):
        query = "SELECT * FROM authors WHERE id = %(id)s;"
        results = connect_to_mysql(cls.DB).query_db(query, data)
        if results:
            return cls(results[0])
        return None
    
    @classmethod
    def update(cls, data):
        query = """
                UPDATE authors SET first_name=%(first_name)s,last_name=%(last_name)s 
                WHERE id = %(id)s;
                """
        return connect_to_mysql(cls.DB).query_db(query, data)
    
    @classmethod
    def delete_author(cls, data):
        query = "DELETE FROM authors WHERE id = %(id)s;"
        return connect_to_mysql(cls.DB).query_db(query, data)
    
    @staticmethod
    def validate_author(author):
        is_valid = True # we assume this is true
        if len(author['first_name']) < 3:
            flash("First name must be at least 3 characters.")
            is_valid = False
        if len(author['last_name']) < 3:
            flash("Last name must be at least 3 characters.")
            is_valid = False
        return is_valid
