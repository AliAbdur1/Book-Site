from flask import render_template, redirect, request, flash, session
from flask_app import app
from flask_app.models.recommendations_model import BookRecommendation
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/book/<int:book_id>/recommend', methods=['POST'])
@login_required
def recommend_book(book_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    data = {
        'sender_id': session['user_id'],
        'receiver_id': request.form['receiver_id'],
        'book_id': book_id,
        'message': request.form.get('message', '')  # Make message optional
    }
    
    BookRecommendation.create_recommendation(data)
    flash('Book recommendation sent successfully!', 'success')
    return redirect(f'/book/{book_id}')

@app.route('/recommendation/<int:recommendation_id>/read', methods=['POST'])
@login_required
def mark_recommendation_read(recommendation_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    BookRecommendation.mark_as_read(recommendation_id)
    flash('Recommendation marked as read', 'success')
    return redirect(request.referrer)

@app.route('/recommendation/<int:recommendation_id>/delete', methods=['POST'])
@login_required
def delete_recommendation(recommendation_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    BookRecommendation.delete_recommendation(recommendation_id, session['user_id'])
    flash('Recommendation deleted', 'success')
    return redirect(request.referrer)
