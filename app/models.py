from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(10), default='student')
    profile_pic = db.Column(db.String(255), nullable=True, default='default.jpg')
    total_score = db.Column(db.Integer, default=0)
    submissions = db.relationship('Submission', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    description = db.Column(db.Text)
    max_score = db.Column(db.Integer)
    submissions = db.relationship('Submission', backref='assignment', lazy='dynamic')

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
    code_text = db.Column(db.Text)
    score = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class Day(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    lessons = db.relationship('Lesson', backref='day', lazy='dynamic')
    programs = db.relationship('Program', backref='day', lazy='dynamic')

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    day_id = db.Column(db.Integer, db.ForeignKey('day.id'))
    html_file = db.Column(db.String(120), nullable=True)
    notes = db.relationship('Note', backref='lesson', lazy='dynamic')

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    day_id = db.Column(db.Integer, db.ForeignKey('day.id'))
    python_file = db.Column(db.String(120), nullable=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    content = db.Column(db.Text)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)