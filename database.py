from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """Model for storing user information"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    medications = db.relationship('Medication', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Medication(db.Model):
    """Model for storing medication information"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reminders = db.relationship('Reminder', backref='medication', lazy=True, cascade='all, delete-orphan')
    doses = db.relationship('Dose', backref='medication', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Medication {self.name}>'


class Reminder(db.Model):
    """Model for storing reminder schedules"""
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    reminder_time = db.Column(db.String(5), nullable=False)  # HH:MM format
    frequency = db.Column(db.String(20), nullable=False)  # daily, weekly, custom
    days_of_week = db.Column(db.String(50))  # comma-separated: 0=Mon, 6=Sun
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Reminder {self.reminder_time}>'


class Dose(db.Model):
    """Model for tracking when medications were taken"""
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Dose {self.medication_id} at {self.taken_at}>'


def init_db(app):
    """Initialize the database"""
    with app.app_context():
        db.create_all()
