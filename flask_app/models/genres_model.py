from flask_app.config.mysqlconnection import connect_to_mysql

class Genre:
    DB = 'mydb'

    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        
    @classmethod
    def get_all_genres(cls):
        query = "SELECT * FROM genres;"
        results = connect_to_mysql(cls.DB).query_db(query)
        genres = []
        for genre in results:
            genres.append(cls(genre))
        return genres

    @classmethod
    def create_genre(cls, data):
        query = "INSERT INTO genres (name, created_at, updated_at) VALUES (%(name)s, NOW(), NOW());"
        # data is a dictionary that will be passed into the save method from server.py
        return connect_to_mysql(cls.DB).query_db(query, data)