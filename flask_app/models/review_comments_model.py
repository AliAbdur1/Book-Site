from flask_app.config.mysqlconnection import connect_to_mysql
from flask_app.models import users_model

class ReviewComment:
    DB = 'mydb'
    
    def __init__(self, data):
        self.id = data['id']
        self.comment = data['comment']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']
        self.review_id = data['review_id']
        self.user = None  # Will hold the user who made the comment
    
    @classmethod
    def create_comment(cls, data):
        query = """
            INSERT INTO review_comments (comment, user_id, review_id, created_at, updated_at)
            VALUES (%(comment)s, %(user_id)s, %(review_id)s, NOW(), NOW());
        """
        return connect_to_mysql(cls.DB).query_db(query, data)
    
    @classmethod
    def get_comments_by_review(cls, review_id):
        query = """
            SELECT rc.*, u.first_name, u.last_name, u.email, u.role, u.profile_photo
            FROM review_comments rc
            JOIN users u ON rc.user_id = u.id
            WHERE rc.review_id = %(review_id)s
            ORDER BY rc.created_at DESC;
        """
        results = connect_to_mysql(cls.DB).query_db(query, {'review_id': review_id})
        comments = []
        for row in results:
            comment = cls(row)
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
            comment.user = users_model.User(user_data)
            comments.append(comment)
        return comments
    
    @classmethod
    def delete_comment(cls, comment_id, user_id):
        """Delete a comment if it belongs to the user"""
        query = """
            DELETE FROM review_comments 
            WHERE id = %(comment_id)s AND user_id = %(user_id)s;
        """
        data = {
            'comment_id': comment_id,
            'user_id': user_id
        }
        return connect_to_mysql(cls.DB).query_db(query, data)
