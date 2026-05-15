"""
E-commerce API Routes
WARNING: This file contains intentional security vulnerabilities for testing purposes
"""

from flask import Flask, request, jsonify, session
import sqlite3
import os
import subprocess

app = Flask(__name__)
app.secret_key = 'insecure-secret-key-123'  # VULNERABILITY: Weak secret key

# VULNERABILITY: Deprecated API v1 endpoints still active
@app.route('/api/v1/users', methods=['GET'])
def get_users_v1():
    """
    DEPRECATED: Use /api/v3/users instead
    This endpoint will be removed on 2024-12-31
    """
    # VULNERABILITY: No authentication required
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # VULNERABILITY: SQL Injection - user input not sanitized
    user_id = request.args.get('id', '')
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL INJECTION
    
    cursor.execute(query)
    users = cursor.fetchall()
    conn.close()
    
    # VULNERABILITY: Returns sensitive data including passwords
    return jsonify({'users': users})


@app.route('/api/v1/search', methods=['GET'])
def search_users_v1():
    """
    DEPRECATED: Legacy search endpoint
    """
    # VULNERABILITY: No authentication
    search_term = request.args.get('q', '')
    
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    # VULNERABILITY: SQL Injection via LIKE clause
    query = f"SELECT * FROM users WHERE name LIKE '%{search_term}%'"
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    return jsonify({'results': results})


@app.route('/api/v1/admin/users', methods=['GET', 'POST', 'DELETE'])
def admin_users_v1():
    """
    DEPRECATED: Admin endpoint without proper authentication
    """
    # VULNERABILITY: No authentication check
    # VULNERABILITY: No authorization check
    
    if request.method == 'DELETE':
        user_id = request.args.get('id')
        conn = sqlite3.connect('ecommerce.db')
        cursor = conn.cursor()
        # VULNERABILITY: SQL Injection
        cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
        conn.commit()
        conn.close()
        return jsonify({'message': 'User deleted'})
    
    return jsonify({'message': 'Admin endpoint'})


@app.route('/api/v2/payments', methods=['POST'])
def process_payment_v2():
    """
    Payment processing endpoint
    """
    # VULNERABILITY: Weak authentication
    api_key = request.headers.get('X-API-Key')
    if api_key != 'simple-api-key-123':  # WEAK API KEY
        return jsonify({'error': 'Unauthorized'}), 401
    
    payment_data = request.json
    
    # VULNERABILITY: Logs sensitive payment information
    print(f"Processing payment: {payment_data}")  # LOGS CREDIT CARD DATA
    app.logger.info(f"Payment details: {payment_data}")  # LOGS TO FILE
    
    # VULNERABILITY: No input validation
    amount = payment_data.get('amount')
    card_number = payment_data.get('card_number')
    cvv = payment_data.get('cvv')
    
    return jsonify({
        'status': 'success',
        'transaction_id': '12345',
        'card_last_four': card_number[-4:]  # EXPOSES CARD INFO
    })


@app.route('/api/v3/users/<int:user_id>', methods=['GET'])
def get_user_v3(user_id):
    """
    Current API version - but still has vulnerabilities
    """
    # VULNERABILITY: Weak authentication
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # VULNERABILITY: No authorization check - any authenticated user can access any user's data
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        # VULNERABILITY: Returns sensitive data
        return jsonify({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'password_hash': user[3],  # EXPOSES PASSWORD HASH
            'ssn': user[4],  # EXPOSES SSN
            'credit_card': user[5],  # EXPOSES CREDIT CARD
            'address': user[6]
        })
    
    return jsonify({'error': 'User not found'}), 404


@app.route('/api/v3/export', methods=['GET'])
def export_data():
    """
    Data export endpoint
    """
    # VULNERABILITY: No rate limiting
    # VULNERABILITY: Weak authentication
    api_key = request.headers.get('Authorization')
    
    if not api_key:
        return jsonify({'error': 'No API key provided'}), 401
    
    # VULNERABILITY: Allows export of all data without proper authorization
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    table = request.args.get('table', 'users')
    # VULNERABILITY: SQL Injection via table name
    cursor.execute(f"SELECT * FROM {table}")  # SQL INJECTION
    data = cursor.fetchall()
    conn.close()
    
    # VULNERABILITY: Logs export activity with sensitive info
    app.logger.info(f"User exported {len(data)} records from {table}")
    
    return jsonify({'data': data, 'count': len(data)})


@app.route('/api/v3/upload', methods=['POST'])
def upload_file():
    """
    File upload endpoint
    """
    # VULNERABILITY: No authentication
    # VULNERABILITY: No file type validation
    # VULNERABILITY: No file size limit
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    filename = file.filename  # VULNERABILITY: No sanitization
    
    # VULNERABILITY: Path traversal possible
    upload_path = os.path.join('/uploads', filename)
    file.save(upload_path)
    
    return jsonify({'message': 'File uploaded', 'path': upload_path})


@app.route('/api/v3/execute', methods=['POST'])
def execute_command():
    """
    DANGEROUS: Command execution endpoint
    """
    # VULNERABILITY: Command injection
    # VULNERABILITY: No authentication
    
    command = request.json.get('command', '')
    
    # VULNERABILITY: Direct command execution
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    return jsonify({
        'stdout': result.stdout,
        'stderr': result.stderr,
        'returncode': result.returncode
    })


@app.route('/api/v3/debug', methods=['GET'])
def debug_info():
    """
    Debug endpoint - should not be in production
    """
    # VULNERABILITY: Debug endpoint exposed in production
    # VULNERABILITY: No authentication
    
    return jsonify({
        'environment': dict(os.environ),  # EXPOSES ALL ENV VARS
        'config': {
            'database': app.config.get('DATABASE_URI'),
            'secret_key': app.config.get('SECRET_KEY'),
            'api_keys': app.config.get('API_KEYS')
        },
        'session': dict(session),  # EXPOSES SESSION DATA
        'headers': dict(request.headers)
    })


@app.route('/api/v3/logs', methods=['GET'])
def get_logs():
    """
    Log viewing endpoint
    """
    # VULNERABILITY: No authentication
    # VULNERABILITY: Exposes sensitive log data
    
    log_file = request.args.get('file', 'app.log')
    
    # VULNERABILITY: Path traversal
    log_path = f'/var/log/{log_file}'
    
    try:
        with open(log_path, 'r') as f:
            logs = f.read()
        return jsonify({'logs': logs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v3/backup', methods=['POST'])
def create_backup():
    """
    Database backup endpoint
    """
    # VULNERABILITY: Weak authentication
    if request.headers.get('X-Admin-Token') != 'admin-token-123':
        return jsonify({'error': 'Unauthorized'}), 401
    
    # VULNERABILITY: Command injection via backup filename
    backup_name = request.json.get('name', 'backup')
    command = f"pg_dump ecommerce_db > /backups/{backup_name}.sql"
    
    os.system(command)  # COMMAND INJECTION
    
    return jsonify({'message': 'Backup created', 'file': f'{backup_name}.sql'})


@app.route('/api/v1/legacy/auth', methods=['POST'])
def legacy_auth():
    """
    DEPRECATED: Legacy authentication endpoint
    Uses weak authentication mechanism
    """
    # VULNERABILITY: Accepts credentials in GET parameters
    username = request.args.get('username') or request.json.get('username')
    password = request.args.get('password') or request.json.get('password')
    
    # VULNERABILITY: Logs credentials
    app.logger.info(f"Login attempt: {username}:{password}")
    
    # VULNERABILITY: Weak password check
    if username == 'admin' and password == 'admin123':
        session['user_id'] = 1
        session['role'] = 'admin'
        return jsonify({'token': 'simple-jwt-token-12345'})  # WEAK TOKEN
    
    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/v2/users/password-reset', methods=['POST'])
def password_reset():
    """
    Password reset endpoint
    """
    email = request.json.get('email')
    
    # VULNERABILITY: No rate limiting - allows brute force
    # VULNERABILITY: Reveals if email exists
    
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        # VULNERABILITY: Predictable reset token
        reset_token = f"reset_{user[0]}_12345"
        return jsonify({
            'message': 'Reset email sent',
            'token': reset_token  # EXPOSES TOKEN
        })
    else:
        return jsonify({'error': 'Email not found'}), 404  # REVEALS EMAIL EXISTENCE


# VULNERABILITY: CORS allows all origins
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response


if __name__ == '__main__':
    # VULNERABILITY: Debug mode enabled
    # VULNERABILITY: Runs on all interfaces
    app.run(debug=True, host='0.0.0.0', port=5000)

# Made with Bob
