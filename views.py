from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Feedback
from . import db
import json
from flask_wtf.csrf import generate_csrf

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        if not name or not email or not message:
            flash('Please fill in all fields', category='error')
        else:
            # Here you would typically save the contact form data or send an email
            flash('Message sent successfully!', category='success')
            
    return render_template("home.html", user=current_user, csrf_token=generate_csrf())

@views.route('/feedback', methods=['POST'])
@login_required
def submit_feedback():
    if request.method == 'POST':
        rating = request.form.get('rating')
        category = request.form.get('category')
        feedback_text = request.form.get('feedback')
        suggestions = request.form.get('suggestions')

        if not rating or not category or not feedback_text:
            flash('Please fill in all required fields!', category='error')
        else:
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    new_feedback = Feedback(
                        rating=rating,
                        category=category,
                        feedback_text=feedback_text,
                        suggestions=suggestions,
                        user_id=current_user.id
                    )
                    db.session.add(new_feedback)
                    db.session.commit()
                    flash('Thank you for your feedback!', category='success')
                    return redirect(url_for('views.home'))
                else:
                    flash('Invalid rating value!', category='error')
            except ValueError:
                flash('Invalid rating format!', category='error')
    
    return redirect(url_for('views.home'))

@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    try:
        note = json.loads(request.data)
        noteId = note['noteId']
        note = Note.query.get(noteId)
        if note:
            if note.user_id == current_user.id:
                db.session.delete(note)
                db.session.commit()
                return jsonify({})
            else:
                return jsonify({"error": "Unauthorized"}), 403
        return jsonify({"error": "Note not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
