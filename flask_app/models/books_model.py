from flask_app.config.mysqlconnection import connect_to_mysql
from flask_app.models import authors_model
from flask_app.models import reviews_model

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
        self.publisher_id = data['publisher_id']
        self.this_book_author = []
        self.this_Books_many_Authors = []
        self.this_author_here = []
        self.reviews = []  # Will hold the book's reviews

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
    def get_books_by_author_count(cls, min_authors=0):
        """
        Get books that have at least min_authors number of authors.
        Args:
            min_authors (int): Minimum number of authors a book should have (default 0 returns all books)
        Returns:
            list: List of Book objects with their associated authors
        """
        query = """
            SELECT b.*, a.id as author_id, a.first_name, a.last_name,
            COUNT(ba.author_id) as author_count
            FROM books b
            LEFT JOIN book_authors ba ON b.id = ba.book_id
            LEFT JOIN authors a ON ba.author_id = a.id
            GROUP BY b.id
            HAVING author_count >= %(min_authors)s;
        """
        results = connect_to_mysql(cls.DB).query_db(query, {'min_authors': min_authors})
        
        if not results:
            return []
            
        books = []
        current_book = None
        
        for row in results:
            if not current_book or current_book.id != row['id']:
                book_data = {
                    "id": row['id'],
                    "title": row['title'],
                    "description": row['description'],
                    "page_count": row['page_count'],
                    "created_at": row['created_at'],
                    "updated_at": row['updated_at'],
                    "genre_id": row['genre_id'],
                    "publisher_id": row['publisher_id']
                }
                current_book = cls(book_data)
                books.append(current_book)
            
            if row['author_id']:
                author_data = {
                    "id": row['author_id'],
                    "first_name": row['first_name'],
                    "last_name": row['last_name']
                }
                current_book.this_Books_many_Authors.append(authors_model.Author(author_data))
        
        return books

    @classmethod
    def get_books_by_author_id(cls, data):
        query = """
        SELECT books.*, authors.first_name, authors.last_name
        FROM books
        JOIN book_authors ON books.id = book_authors.book_id
        JOIN authors ON authors.id = book_authors.author_id
        WHERE authors.id = %(id)s;
        """
        results = connect_to_mysql(cls.DB).query_db(query, data)
        books = []
        if results:
            for row in results:
                books.append(cls(row))
        return books

    @classmethod
    def get_books_by_author(cls, author_id):
        query = """
            SELECT books.* FROM books
            JOIN book_authors ON books.id = book_authors.book_id
            WHERE book_authors.author_id = %(author_id)s;
        """
        results = connect_to_mysql(cls.DB).query_db(query, {'author_id': author_id})
        books = []
        if results:
            for row in results:
                books.append(cls(row))
        return books

    @classmethod
    def create_book(cls, data):
        try:
            # First create the book
            query = """
                    INSERT INTO books (title, description, page_count, created_at, updated_at, genre_id, publisher_id) 
                    VALUES (%(title)s, %(description)s, %(page_count)s, NOW(), NOW(), %(genre_id)s, %(publisher_id)s);
                    """
            book_id = connect_to_mysql(cls.DB).query_db(query, data)
            
            # Then create book-author relationships for each author
            if book_id and 'author_ids' in data and data['author_ids']:
                for author_id in data['author_ids']:
                    cls.add_book_author(book_id, author_id)
            
            return book_id
        except Exception as e:
            print(f"Error creating book: {str(e)}")
            return False

    @classmethod
    def add_book_author(cls, book_id, author_id):
        """Add an author to a book"""
        try:
            query = """
                    INSERT INTO book_authors (book_id, author_id) 
                    VALUES (%(book_id)s, %(author_id)s);
                    """
            data = {
                'book_id': book_id,
                'author_id': author_id
            }
            return connect_to_mysql(cls.DB).query_db(query, data)
        except Exception as e:
            print(f"Error adding book-author relationship: {str(e)}")
            return False
    
    @classmethod
    def get_book_by_id(cls, book_id):
        query = "SELECT * FROM books WHERE id = %(id)s;"
        data = {"id": book_id}
        results = connect_to_mysql(cls.DB).query_db(query, data)
        return cls(results[0])
    
    @classmethod
    def get_book_with_reviews(cls, book_id):
        """Get a book with its reviews and authors"""
        data = {"id": book_id}
        book = cls.get_book_w_author(data)
        if book:
            book.reviews = reviews_model.Review.get_book_reviews(book_id)
        return book
    
    @classmethod
    def update(cls, data):
        try:
            # First update the book's basic information
            query = """
                    UPDATE books 
                    SET title = %(title)s, description = %(description)s, 
                        page_count = %(page_count)s, genre_id = %(genre_id)s, 
                        publisher_id = %(publisher_id)s, updated_at = NOW()
                    WHERE id = %(id)s;
                    """
            connect_to_mysql(cls.DB).query_db(query, data)
            
            # Then update the book's authors
            if 'author_ids' in data:
                # First remove all existing book-author relationships
                cls.remove_all_book_authors(data['id'])
                
                # Then add the new relationships
                for author_id in data['author_ids']:
                    cls.add_book_author(data['id'], author_id)
            
            return True
        except Exception as e:
            print(f"Error updating book: {str(e)}")
            return False

    @classmethod
    def remove_all_book_authors(cls, book_id):
        """Remove all authors from a book"""
        query = "DELETE FROM book_authors WHERE book_id = %(book_id)s;"
        return connect_to_mysql(cls.DB).query_db(query, {'book_id': book_id})

    @classmethod
    def delete_book(cls, book_id):
        query  = "DELETE FROM books WHERE id = %(id)s;"
        data = {'id': book_id}
        return connect_to_mysql(cls.DB).query_db(query, data)
    
    @classmethod
    def search_by_title(cls, title):
        query = """SELECT * FROM books 
                WHERE title LIKE %(search_term)s;"""
        results = connect_to_mysql(cls.DB).query_db(query, {'search_term': f'%{title}%'})
        books = []
        for book in results:
            books.append(cls(book))
        return books

    @classmethod
    def search_by_author(cls, search_term):
        if not search_term:
            return []
        
        query = """SELECT DISTINCT
                books.*, 
                GROUP_CONCAT(authors.first_name, ' ', authors.last_name) as author_names
            FROM books
            JOIN book_authors ON books.id = book_authors.book_id
            JOIN authors ON book_authors.author_id = authors.id
            WHERE authors.first_name LIKE %(search)s
            OR authors.last_name LIKE %(search)s
            GROUP BY books.id;"""
        
        results = connect_to_mysql(cls.DB).query_db(
            query, 
            {'search': f'%{search_term}%'}
        )
        
        if not results:
            return []
            
        return [cls(book) for book in results]

    @classmethod
    def search_by_genre(cls, genre_id):
        query = """SELECT * FROM books 
                WHERE genre_id = %(genre_id)s;"""
        results = connect_to_mysql(cls.DB).query_db(query, {'genre_id': genre_id})
        books = []
        for book in results:
            books.append(cls(book))
        return books

    @classmethod
    def search_by_page_count(cls, page_count):
        query = """SELECT * FROM books 
                WHERE page_count = %(page_count)s;"""
        results = connect_to_mysql(cls.DB).query_db(query, {'page_count': page_count})
        books = []
        for book in results:
            books.append(cls(book))
        return books

    @classmethod
    def get_book_authors(cls, book_id):
        """Get all authors for a book"""
        query = """
                SELECT authors.* 
                FROM authors 
                JOIN book_authors ON authors.id = book_authors.author_id 
                WHERE book_authors.book_id = %(book_id)s;
                """
        results = connect_to_mysql(cls.DB).query_db(query, {'book_id': book_id})
        return [authors_model.Author(author) for author in results] if results else []