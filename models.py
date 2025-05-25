from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    failed_attempts = db.Column(db.Integer, default=0)
    is_locked = db.Column(db.Boolean, default=False)
    lockout_until = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def lock_account(self):
        self.is_locked = True
        self.lockout_until = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()

    def unlock_account(self):
        if self.lockout_until and datetime.utcnow() >= self.lockout_until:
            self.is_locked = False
            self.failed_attempts = 0
            self.lockout_until = None
            db.session.commit()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  
    failed_attempts = db.Column(db.Integer, default=0)
    is_locked = db.Column(db.Boolean, default=False)
    lockout_until = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def lock_account(self):
        self.is_locked = True
        self.lockout_until = datetime.utcnow() + timedelta(minutes=10) 
        db.session.commit()

    def unlock_account(self):
        if self.lockout_until and datetime.utcnow() >= self.lockout_until:
            self.is_locked = False
            self.failed_attempts = 0
            self.lockout_until = None
            db.session.commit()

class SubmittedTitle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_text = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    similarity_score = db.Column(db.Float)  
    matched_title = db.Column(db.String(500))  
    matched_source = db.Column(db.String(100))  
    disallowed_words = db.Column(db.String(500))  
    common_patterns = db.Column(db.String(500))
    verification_probability = db.Column(db.Float, default=0.0)  
    
    user = db.relationship('User', backref='submitted_titles')

class Prefix(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100), unique=True, nullable=False)

class Suffix(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(100), unique=True, nullable=False)

class DisallowedWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), unique=True, nullable=False)
