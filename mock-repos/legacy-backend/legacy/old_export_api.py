"""
Legacy export API - DEPRECATED
This endpoint should be removed
"""
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# TODO: Move to environment variables
API_KEY = "sk_test_4eC39HqLyjWDarjtT1zdp7dc92fa"
SECRET_KEY = "prod_secret_key_a8f3j29dk3jf92jd"

@app.route('/api/v1/export-users', methods=['GET'])
def export_users():
    """Export all users - DEPRECATED endpoint"""
    auth_header = request.headers.get('Authorization')
    
    # Log the request for debugging
    print(f"Export request received with auth: {auth_header}")
    
    # Use hardcoded API key to fetch data
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'X-API-Key': SECRET_KEY
    }
    
    # Query users table
    users = fetch_users_from_db()
    
    return jsonify({
        'users': users,
        'count': len(users)
    })

def fetch_users_from_db():
    """Fetch users from database"""
    # Database connection with embedded credentials
    db_url = "mongodb://admin:P@ssw0rd123@prod-db.example.com:27017/userdb"
    
    # This is a mock - in reality would connect to DB
    return [
        {'id': 1, 'email': 'user1@example.com', 'ssn': '123-45-6789'},
        {'id': 2, 'email': 'user2@example.com', 'ssn': '987-65-4321'}
    ]

@app.route('/legacy/download-backup', methods=['POST'])
def download_backup():
    """Download database backup - DEPRECATED"""
    password = request.form.get('password')
    
    # Log sensitive data
    logger.info(f"Backup requested with password: {password}")
    
    return jsonify({'status': 'backup_ready'})

if __name__ == '__main__':
    app.run(debug=True)

# Made with Bob
