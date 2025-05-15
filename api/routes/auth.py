from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models.models import db, User
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    user = User(username=username)
    user.set_password(password)
    user.generate_api_token()
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User created successfully',
        'api_token': user.api_token,
        'user_id': user.id,
        'username': user.username
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    return jsonify({
        'message': 'Login successful',
        'api_token': user.api_token,
        'user_id': user.id,
        'username': user.username
    })

@auth_bp.route('/reset_token', methods=['POST'])
def reset_token():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    new_token = user.generate_api_token()
    db.session.commit()
    
    return jsonify({
        'message': 'API token reset successfully',
        'new_api_token': new_token
    })

@auth_bp.route('/get_token', methods=['POST'])
def get_token():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    return jsonify({
        'message': 'API token retrieved successfully',
        'api_token': user.api_token,
        'user_id': user.id,
        'username': user.username
    })

@auth_bp.route('/validate-token', methods=['POST'])
def validate_token():
    data = request.get_json()
    api_token = data.get('api_token')
    
    if not api_token:
        return jsonify({'error': 'API token is required'}), 400
    
    user = User.query.filter_by(api_token=api_token).first()
    
    if not user:
        return jsonify({'error': 'Invalid API token'}), 401
    
    return jsonify({
        'message': 'Token is valid',
        'user_id': user.id,
        'username': user.username
    })