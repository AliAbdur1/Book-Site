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
            SELECT * FROM publishers
            LEFT JOIN authors ON authors.publisher_id = publishers.id
            WHERE publishers.id = %(id)s;
        """
        results = connect_to_mysql(cls.DB).query_db(query, data)
        if not results:
            return None
        publisher = cls(results[0])
        for row in results:
            author_data = {
                "id": row["authors.id"],
                "first_name": row["authors.first_name"],
                "last_name": row["authors.last_name"],
                "created_at": row["authors.created_at"],
                "updated_at": row["authors.updated_at"]
            }
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
    def delete_publisher(cls, data):
        query = "DELETE FROM publishers WHERE id = %(id)s;"
        return connect_to_mysql(cls.DB).query_db(query, data)
    
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
