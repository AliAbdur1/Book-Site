from flask_app.config.mysqlconnection import connect_to_mysql
from flask_app.models import authors_model
from flask import flash

class Publisher:
    DB = 'mydb'
    
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.address = data['address']
        self.city = data['city']
        self.state = data['state']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.author_id = data['author_id']
        self.authors = []

    @classmethod
    def get_all_publishers(cls):
        query = "SELECT * FROM publishers;"
        results = connect_to_mysql(cls.DB).query_db(query)
        publishers = []
        for row in results:
            publishers.append(cls(row))
        return publishers
    
    @classmethod
    def get_publisher_with_authors(cls, data):
        query = """
            SELECT publishers.*, authors.id AS author_id, authors.first_name, authors.last_name,
                   authors.created_at AS author_created_at, authors.updated_at AS author_updated_at
            FROM publishers
            LEFT JOIN author_publishers ON publishers.id = author_publishers.publishers_id
            LEFT JOIN authors ON author_publishers.authors_id = authors.id
            WHERE publishers.id = %(id)s;
        """
        results = connect_to_mysql(cls.DB).query_db(query, data)
        if not results:
            return None
        publisher = cls(results[0])
        for row in results:
            if row['author_id']:
                author_data = {
                    "id": row["author_id"],
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "created_at": row["author_created_at"],
                    "updated_at": row["author_updated_at"]
                }
                print(author_data)
                publisher.authors.append(authors_model.Author(author_data))
        return publisher

    @classmethod
    def create_publisher(cls, data):
        query = """
            INSERT INTO publishers (name, address, city, state, created_at, updated_at, author_id)
            VALUES (%(name)s, %(address)s, %(city)s, %(state)s, NOW(), NOW(), %(author_id)s);
        """
        return connect_to_mysql(cls.DB).query_db(query, data)

    @classmethod
    def get_publisher_by_id(cls, publisher_id):
        query = "SELECT * FROM publishers WHERE id = %(id)s;"
        data = {"id": publisher_id}
        result = connect_to_mysql(cls.DB).query_db(query, data)
        if result:
            return cls(result[0])
        return None

    @classmethod
    def update_publisher(cls, data):
        query = """
            UPDATE publishers SET name=%(name)s, address=%(address)s, city=%(city)s, state=%(state)s,
            updated_at=NOW() WHERE id = %(id)s;
        """
        return connect_to_mysql(cls.DB).query_db(query, data)

    @classmethod
    def delete_publisher(cls, publisher_id):
        try:
            # First, update books to set publisher_id to NULL
            update_books_query = "UPDATE books SET publisher_id = NULL WHERE publisher_id = %(id)s;"
            data = {"id": publisher_id}
            connect_to_mysql(cls.DB).query_db(update_books_query, data)
            
            # Then delete from author_publishers junction table
            delete_author_publishers_query = "DELETE FROM author_publishers WHERE publishers_id = %(id)s;"
            connect_to_mysql(cls.DB).query_db(delete_author_publishers_query, data)
            
            # Finally delete the publisher
            delete_publisher_query = "DELETE FROM publishers WHERE id = %(id)s;"
            return connect_to_mysql(cls.DB).query_db(delete_publisher_query, data)
        except Exception as e:
            print(f"Error deleting publisher: {str(e)}")
            return False
    
    @classmethod
    def add_author(cls, data):
        try:
            # Check if relationship already exists
            check_query = """
                SELECT * FROM author_publishers 
                WHERE authors_id = %(author_id)s AND publishers_id = %(publisher_id)s;
            """
            result = connect_to_mysql(cls.DB).query_db(check_query, data)
            if result:
                return False
            
            # Add the relationship
            query = """
                INSERT INTO author_publishers (authors_id, publishers_id, created_at, updated_at)
                VALUES (%(author_id)s, %(publisher_id)s, NOW(), NOW());
            """
            connect_to_mysql(cls.DB).query_db(query, data)
            return True
        except Exception as e:
            print(f"Error adding author to publisher: {str(e)}")
            return False

    @classmethod
    def remove_author(cls, data):
        try:
            query = """
                DELETE FROM author_publishers 
                WHERE authors_id = %(author_id)s AND publishers_id = %(publisher_id)s;
            """
            connect_to_mysql(cls.DB).query_db(query, data)
            return True
        except Exception as e:
            print(f"Error removing author from publisher: {str(e)}")
            return False

    @staticmethod
    def validate_publisher(publisher):
        is_valid = True # we assume this is true
        if len(publisher['name']) < 3:
            flash("name must be at least 3 characters.")
            is_valid = False
        if len(publisher['address']) < 3:
            flash("address must be at least 3 characters.")
            is_valid = False
        if len(publisher['city']) < 2:
            flash("city must be at least 2 characters.")
            is_valid = False
        if len(publisher['state']) < 2:
            flash("state must be at least 2 characters.")
            is_valid = False
        return is_valid
