from flask_app.config.mysqlconnection import connect_to_mysql
from flask_app.models import users_model, review_comments_model

class Review:
    DB = 'mydb'
    
    def __init__(self, data):
        self.id = data['id']
        self.comment = data['comment']
        self.stars = data['stars']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']
        self.book_id = data['book_id']
        self.user = None  # Will hold the user who wrote the review
        self.comments = []  # Will hold comments on this review
    
    @classmethod
    def create_review(cls, data):
        query = """
                INSERT INTO reviews (comment, stars, user_id, book_id, created_at, updated_at) 
                VALUES (%(comment)s, %(stars)s, %(user_id)s, %(book_id)s, NOW(), NOW());
                """
        return connect_to_mysql(cls.DB).query_db(query, data)
    
    @classmethod
    def get_book_reviews(cls, book_id):
        query = """
                SELECT r.*, u.first_name, u.last_name, u.email, u.role, u.profile_photo
                FROM reviews r
                JOIN users u ON r.user_id = u.id
                WHERE r.book_id = %(book_id)s
                ORDER BY r.created_at DESC;
                """
        results = connect_to_mysql(cls.DB).query_db(query, {'book_id': book_id})
        reviews = []
        for row in results:
            review = cls(row)
            user_data = {
                'id': row['user_id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'email': row['email'],
                'role': row['role'],
                'profile_photo': row['profile_photo'],
                'password': '',  # Not needed for display
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            review.user = users_model.User(user_data)
            # Get comments for this review
            review.comments = review_comments_model.ReviewComment.get_comments_by_review(review.id)
            reviews.append(review)
        return reviews
    
    @classmethod
    def get_all_reviews(cls):
        query = "SELECT * FROM reviews;"
        results = connect_to_mysql(cls.DB).query_db(query)
        reviews = []
        for row in results:
            reviews.append(cls(row))
        return reviews
    
    @classmethod
    def get_review_by_id(cls, review_id):
        query = "SELECT * FROM reviews WHERE id = %(id)s;"
        results = connect_to_mysql(cls.DB).query_db(query, {'id': review_id})
        if results:
            return cls(results[0])
        return None
    
    @classmethod
    def update_review(cls, review_id, user_id, comment, stars):
        """Update a review if it belongs to the user"""
        query = "UPDATE reviews SET comment = %(comment)s, stars = %(stars)s, updated_at = NOW() WHERE id = %(id)s AND user_id = %(user_id)s;"
        return connect_to_mysql(cls.DB).query_db(query, {'id': review_id, 'comment': comment, 'stars': stars, 'user_id': user_id})
    
    
    @classmethod
    def delete_review(cls, review_id, user_id):
        """Delete a review if it belongs to the user"""
        query = "DELETE FROM reviews WHERE id = %(id)s AND user_id = %(user_id)s;"
        return connect_to_mysql(cls.DB).query_db(query, {'id': review_id, 'user_id': user_id})
