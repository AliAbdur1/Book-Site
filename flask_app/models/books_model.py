from flask_app.config.mysqlconnection import connect_to_mysql
from flask_app.models import authors_model

class Book:
    DB = 'mydb'
    
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.description = data['description']
        self.page_count = data['page_count']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.genre_id = data['genre_id']
        self.author_id = data['author_id']
        self.publisher_id = data['publisher_id']
        self.this_book_author = []
        self.this_Books_many_Authors = []
        self.this_author_here = []

    @classmethod
    def get_all_books(cls):
        query = "SELECT * FROM books;"
        results = connect_to_mysql(cls.DB).query_db(query)
        books = []
        for book in results:
            books.append(cls(book))
        return books
    
    @classmethod
    def get_book_w_author(cls, data):
        query = """
                SELECT books.*, authors.id AS author_id, authors.first_name, authors.last_name, 
                authors.created_at AS author_created_at, authors.updated_at AS author_updated_at
                FROM books
                LEFT JOIN book_authors ON book_authors.book_id = books.id
                LEFT JOIN authors ON book_authors.author_id = authors.id
                WHERE books.id = %(id)s;
                """
        result = connect_to_mysql(cls.DB).query_db(query, data)
        if not result:
            return None
        book = cls(result[0])
        for row in result:
            author_data = {
                "id": row['author_id'],
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "created_at": row['author_created_at'],
                "updated_at": row['author_updated_at']
            }
            book.this_book_author.append(authors_model.Author(author_data))
        return book
    
    @classmethod
    def get_books_with_multiple_authors(cls):
        query = """
                SELECT books.*, authors.id AS author_id, authors.first_name, authors.last_name, 
                authors.created_at AS author_created_at, authors.updated_at AS author_updated_at
                FROM books
                LEFT JOIN book_authors ON book_authors.book_id = books.id
                LEFT JOIN authors ON book_authors.author_id = authors.id
                """
        results = connect_to_mysql(cls.DB).query_db(query)
        if not results:
            return None
        books = []
        current_book = None
        current_book_id = None
        for row in results:
            if row['id'] != current_book_id:
                if current_book:
                    books.append(current_book)
                book_data = {
                    "id": row['id'],
                    "title": row['title'],
                    "description": row['description'],
                    "page_count": row['page_count'],
                    "created_at": row['created_at'],
                    "updated_at": row['updated_at'],
                    "genre_id": row['genre_id'],
                    "author_id": row['author_id'],
                    "publisher_id": row['publisher_id'],
                    "this_Books_many_Authors": []
                }
                current_book = cls(book_data)
                current_book_id = row['id']
            author_data = {
                "id": row['author_id'],
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "created_at": row['author_created_at'],
                "updated_at": row['author_updated_at']
            }
            current_book.this_Books_many_Authors.append(authors_model.Author(author_data))
        if current_book and len(current_book.this_Books_many_Authors) > 1:
            books.append(current_book)
        return books
    
    

# gtp edit to get books with multiple authors vv
    @classmethod
    def get_books_that_have_multiple_authors(cls):
        query = """
                SELECT books.*, authors.id AS this_author_id, authors.first_name, authors.last_name, 
                authors.created_at AS author_created_at, authors.updated_at AS author_updated_at
                FROM books
                LEFT JOIN book_authors ON book_authors.book_id = books.id
                LEFT JOIN authors ON book_authors.author_id = authors.id
                """
        results = connect_to_mysql(cls.DB).query_db(query)
        if not results:
            return None
    
        books = []
        current_book = None
        current_book_id = None
    
        for row in results:
            if row['id'] != current_book_id:
                if current_book:
                    books.append(current_book)
                book_data = {
                    "id": row['id'],
                    "title": row['title'],
                    "description": row['description'],
                    "page_count": row['page_count'],
                    "created_at": row['created_at'],
                    "updated_at": row['updated_at'],
                    "genre_id": row['genre_id'],
                    "publisher_id": row['publisher_id'],
                    "this_Books_many_Authors": []  # Initialize an empty list for authors
                }
                current_book = cls(book_data)
                current_book_id = row['id']
        
            if row['this_author_id'] is not None:
                author_data = {
                    "id": row['this_author_id'],
                    "first_name": row['first_name'],
                    "last_name": row['last_name'],
                    "created_at": row['author_created_at'],
                    "updated_at": row['author_updated_at']
                }
                current_book.this_Books_many_Authors.append(authors_model.Author(author_data))
    
        if current_book and len(current_book.this_Books_many_Authors) > 0:
            books.append(current_book)
    
        return books
    # gtp edit to get books with multiple authors end ^^

    
    @classmethod
    def create_book(cls, data):
        query = "INSERT INTO books (title, description, page_count, created_at, updated_at, genre_id, author_id, publisher_id) VALUES (%(title)s, %(description)s, %(page_count)s, NOW(), NOW(), %(genre_id)s, %(author_id)s, %(publisher_id)s);"
        # data is a dictionary that will be passed into the save method from server.py
        return connect_to_mysql(cls.DB).query_db(query, data)
    
    @classmethod
    def get_book_by_id(cls, book_id):
        query = "SELECT * FROM books WHERE id = %(id)s;"
        data = {"id": book_id}
        results = connect_to_mysql(cls.DB).query_db(query, data)
        return cls(results[0])
    
    @classmethod
    def update(cls,data):
        query = """
                UPDATE books SET title=%(title)s, description=%(description)s, page_count=%(page_count)s
                WHERE id = %(id)s;
                """
        results = connect_to_mysql(cls.DB).query_db(query,data)
        return results
    
    @classmethod
    def delete_user(cls, book_id):
        query  = "DELETE FROM books WHERE id = %(id)s;"
        data = {"id": book_id}
        return connect_to_mysql(cls.DB).query_db(query, data)