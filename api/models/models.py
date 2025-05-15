from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from api.extensions import db  # Import from extensions.py


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(20), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))  # Increased from 128 to 256
    api_token = db.Column(db.String(256))  # Increased from 128 to 256
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # Generate ID if not provided
        if not self.id:
            self.generate_id()
    
    def generate_id(self):
        """Generate a random numeric ID between 10 and 20 digits"""
        import random
        length = random.randint(10, 20)  # Random length between 10 and 20
        self.id = ''.join([str(random.randint(0, 9)) for _ in range(length)])
        
        # Ensure ID is unique
        while User.query.filter_by(id=self.id).first():
            self.id = ''.join([str(random.randint(0, 9)) for _ in range(length)])
    
    def validate_id(self, id):
        """Validate that ID is numeric and between 10-20 digits"""
        if not re.match(r'^\d{10,20}$', str(id)):
            raise ValueError("ID must be 10-20 numeric digits")
        return True
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_api_token(self):
        self.api_token = secrets.token_urlsafe(32)
        return self.api_token

class AvailableAccount(db.Model):
    __tablename__ = 'available_accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    check_date = db.Column(db.String)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'))  # Changed to String
    user = db.relationship('User', backref='available_accounts')

class GeneratedAccount(db.Model):
    __tablename__ = 'generated_accounts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    check_date = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.String(20), db.ForeignKey('users.id'))  # Changed to String
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    gender = db.Column(db.String)
    user = db.relationship('User', backref='generated_accounts')