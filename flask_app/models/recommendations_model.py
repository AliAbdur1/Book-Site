from flask_app.config.mysqlconnection import connect_to_mysql
from flask_app.models import users_model, books_model

class BookRecommendation:
    DB = 'mydb'
    
    def __init__(self, data):
        self.id = data['id']
        self.sender_id = data['sender_id']
        self.receiver_id = data['receiver_id']
        self.book_id = data['book_id']
        self.message = data['message']
        self.created_at = data['created_at']
        self.is_read = data.get('is_read', False)  # Default to False if not present
        self.sender = None
        self.book = None
    
    @classmethod
    def create_recommendation(cls, data):
        print("Creating recommendation with data:", data)  # Debug print
        query = """
            INSERT INTO book_recommendations 
            (sender_id, receiver_id, book_id, message, is_read) 
            VALUES (%(sender_id)s, %(receiver_id)s, %(book_id)s, %(message)s, FALSE);
        """
        return connect_to_mysql(cls.DB).query_db(query, data)
    
    @classmethod
    def get_user_recommendations(cls, user_id):
        print("Getting recommendations for user:", user_id)  # Debug print
        query = """
            SELECT r.*, 
                   s.first_name as sender_first_name, s.last_name as sender_last_name,
                   s.email as sender_email, s.role as sender_role,
                   b.title as book_title, b.description as book_description,
                   b.page_count as book_page_count, b.genre_id as book_genre_id,
                   b.publisher_id as book_publisher_id,
                   b.created_at as book_created_at, b.updated_at as book_updated_at
            FROM book_recommendations r
            JOIN users s ON r.sender_id = s.id
            JOIN books b ON r.book_id = b.id
            WHERE r.receiver_id = %(user_id)s
            ORDER BY r.created_at DESC;
        """
        results = connect_to_mysql(cls.DB).query_db(query, {'user_id': user_id})
        print("Query results:", results)  # Debug print
        
        recommendations = []
        if not results:
            return recommendations
            
        for row in results:
            recommendation = cls(row)
            
            sender_data = {
                'id': row['sender_id'],
                'first_name': row['sender_first_name'],
                'last_name': row['sender_last_name'],
                'email': row['sender_email'],
                'role': row['sender_role'],
                'password': '',  # Not needed for display
                'created_at': row['created_at'],
                'updated_at': row['created_at']
            }
            recommendation.sender = users_model.User(sender_data)
            
            book_data = {
                'id': row['book_id'],
                'title': row['book_title'],
                'description': row['book_description'],
                'page_count': row['book_page_count'],
                'genre_id': row['book_genre_id'],
                'publisher_id': row['book_publisher_id'],
                'created_at': row['book_created_at'],
                'updated_at': row['book_updated_at']
            }
            recommendation.book = books_model.Book(book_data)
            
            recommendations.append(recommendation)
        
        return recommendations
    
    @classmethod
    def mark_as_read(cls, recommendation_id):
        print("Marking recommendation as read:", recommendation_id)  # Debug print
        query = """
            UPDATE book_recommendations 
            SET is_read = TRUE 
            WHERE id = %(recommendation_id)s;
        """
        return connect_to_mysql(cls.DB).query_db(query, {'recommendation_id': recommendation_id})
    
    @classmethod
    def delete_recommendation(cls, recommendation_id, receiver_id):
        print("Deleting recommendation:", recommendation_id)  # Debug print
        query = """
            DELETE FROM book_recommendations 
            WHERE id = %(recommendation_id)s AND receiver_id = %(receiver_id)s;
        """
        return connect_to_mysql(cls.DB).query_db(query, {
            'recommendation_id': recommendation_id,
            'receiver_id': receiver_id
        })
