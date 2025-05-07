from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'  # Указываем имя таблицы явно
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    __tablename__ = 'posts'  # Указываем имя таблицы явно
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    category = db.relationship('Category', backref='posts', lazy=True)

class Category(db.Model):
    __tablename__ = 'categories'  # Указываем имя таблицы явно
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)