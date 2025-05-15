from flask import Blueprint, jsonify, send_file, g ,request
from api.models.models import db, AvailableAccount, GeneratedAccount, User
import pandas as pd
from io import BytesIO
from datetime import datetime, timezone, timedelta
from functools import wraps

accounts_bp = Blueprint('accounts', __name__)

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

@accounts_bp.route('/saved_accounts')
@token_required
def get_saved_accounts():
    try:
        accounts = AvailableAccount.query.filter_by(user_id=g.current_user.id).all()
        accounts_data = [{
            'id': account.id,
            'username': account.username,
            'email': account.email,
            'password': account.password,
            'check_date': account.check_date
        } for account in accounts]
        return jsonify({'accounts': accounts_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@accounts_bp.route('/generated_accounts')
@token_required
def get_generated_accounts():
    try:
        accounts = GeneratedAccount.query.filter_by(
            user_id=g.current_user.id
        ).order_by(GeneratedAccount.check_date.desc()).all()
        
        accounts_data = [{
            'id': account.id,
            'username': account.username,
            'email': account.email,
            'gender': account.gender,
            'first_name':account.first_name,
            'last_name':account.last_name,
            'password': account.password,
            'check_date': account.check_date.strftime("%Y-%m-%d %H:%M:%S")
        } for account in accounts]
        return jsonify({'accounts': accounts_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@accounts_bp.route('/download')
@token_required
def download():
    try:
        saved_accounts = AvailableAccount.query.filter_by(
            user_id=g.current_user.id
        ).all()
        
        if not saved_accounts:
            return jsonify({'error': 'No accounts found'}), 404
        
        data = {
            'Email': [account.email for account in saved_accounts],
            'Password': [account.password for account in saved_accounts]
        }
        df = pd.DataFrame(data)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Accounts')
            for column in df:
                column_width = max(df[column].astype(str).map(len).max(), len(column))
                col_idx = df.columns.get_loc(column)
                writer.sheets['Accounts'].set_column(col_idx, col_idx, column_width)
        
        output.seek(0)
        
        gmt6_time = datetime.now(timezone.utc) + timedelta(hours=6)
        timestamp = gmt6_time.strftime("%I-%M-%S-%p-%d-%m-%Y")
        filename = f"gmail_accounts-{timestamp}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@accounts_bp.route('/delete/<int:account_id>', methods=['DELETE'])
@token_required
def delete_account(account_id):
    try:
        # Check in available accounts first
        account = AvailableAccount.query.filter_by(
            id=account_id,
            user_id=g.current_user.id
        ).first()
        
        if account:
            db.session.delete(account)
            db.session.commit()
            return jsonify({'success': True})
            
        # Check in generated accounts if not found in available
        generated = GeneratedAccount.query.filter_by(
            id=account_id,
            user_id=g.current_user.id
        ).first()
        
        if generated:
            db.session.delete(generated)
            db.session.commit()
            return jsonify({'success': True})
            
        return jsonify({'error': 'Account not found or not owned by user'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500