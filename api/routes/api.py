from flask import Blueprint, jsonify, request, g 
from models.models import db, AvailableAccount, GeneratedAccount, User
from utils.email_checker import get_mx_for_domain, check_email_availability_with_retry
from utils.account_generator import generate_username_from_name ,fetch_random_user
from utils.password_generator import generate_random_password
from datetime import datetime
from functools import wraps


api_bp = Blueprint('api', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'error': 'API token is missing'}), 401
            
        current_user = User.query.filter_by(api_token=token).first()
        
        if not current_user:
            return jsonify({'error': 'Invalid API token'}), 401
            
        g.current_user = current_user
        return f(*args, **kwargs)
    return decorated

@api_bp.route('/generate_single', methods=['POST'])
@token_required
def generate_single():
    mx_host = get_mx_for_domain()
    
    if not mx_host:
        return jsonify({'error': 'Failed to get MX record for Gmail. Try again later.'}), 500
    
    account = try_generate_account(mx_host, g.current_user)
    
    if account:
        return jsonify({'account': account})
    else:
        return jsonify({'error': 'Could not find available account after multiple attempts'}), 500

def try_generate_account(mx_host, user):
    max_attempts = 5
    
    # First fetch random user data
    random_user = fetch_random_user()
    if not random_user:
        return None
    
    first_name = random_user['first_name']
    last_name = random_user['last_name']
    gender = random_user['gender']
    
    for _ in range(max_attempts):
        # Generate username based on name
        username = generate_username_from_name(first_name, last_name)
        email = f"{username}@gmail.com"
        
        if (AvailableAccount.query.filter_by(email=email).first() or 
            GeneratedAccount.query.filter_by(email=email).first()):
            continue
            
        is_available = check_email_availability_with_retry(email, mx_host)
        
        if is_available:
            password = generate_random_password()
            current_date = datetime.now()
            
            account = {
                'username': username,
                'email': email,
                'password': password,
                'check_date': current_date.strftime("%Y-%m-%d %H:%M:%S"),
                'user_id': user.id,
                'first_name': first_name,
                'last_name': last_name,
                'gender': gender
            }
            
            db_account = GeneratedAccount(
                username=username,
                email=email,
                password=password,
                check_date=current_date,
                user_id=user.id,
                first_name=first_name,
                last_name=last_name,
                gender=gender
            )
            db.session.add(db_account)
            db.session.commit()
            
            return account
    
    return None

@api_bp.route('/save_account', methods=['POST'])
@token_required
def save_account():
    try:
        account_data = request.get_json()
        account_data['user_id'] = g.current_user.id
        
        # Check if this is a generated account
        generated = GeneratedAccount.query.filter_by(
            email=account_data['email'],
            user_id=g.current_user.id
        ).first()
        
        if generated:
            db.session.delete(generated)
        
        db_account = AvailableAccount(
            username=account_data['username'],
            email=account_data['email'],
            password=account_data['password'],
            check_date=account_data['check_date'],
            user_id=g.current_user.id
        )
        db.session.add(db_account)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/cancel_generated', methods=['POST'])
@token_required
def cancel_generated():
    try:
        data = request.get_json()
        emails_to_delete = data.get('emails', [])
        deleted_count = 0
        
        for email in emails_to_delete:
            account = GeneratedAccount.query.filter_by(
                email=email,
                user_id=g.current_user.id
            ).first()
            if account:
                db.session.delete(account)
                deleted_count += 1
        
        db.session.commit()
        return jsonify({
            'success': True, 
            'deleted_count': deleted_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500