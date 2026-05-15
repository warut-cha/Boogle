"""
E-commerce Application Configuration
WARNING: This file contains intentional security vulnerabilities for testing purposes
"""

import os

# Database Configuration - VULNERABILITY: Hardcoded credentials
DATABASE_CONFIG = {
    'host': 'prod-db.example.com',
    'port': 5432,
    'database': 'ecommerce_prod',
    'username': 'admin',
    'password': 'P@ssw0rd123!Admin',  # LEAKED SECRET
    'ssl_mode': 'disable'
}

# AWS Configuration - VULNERABILITY: Leaked AWS credentials
AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'  # LEAKED AWS KEY
AWS_SECRET_ACCESS_KEY = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'  # LEAKED AWS SECRET
AWS_REGION = 'us-east-1'
S3_BUCKET = 'customer-data-backup'

# Stripe Payment Configuration - VULNERABILITY: Leaked payment API key
STRIPE_API_KEY = 'sk_live_51HqT2KLkjsdhf8234hsdfKJHSDFkjh234'  # LEAKED STRIPE KEY
STRIPE_WEBHOOK_SECRET = 'whsec_1234567890abcdefghijklmnop'

# JWT Configuration - VULNERABILITY: Weak secret
JWT_SECRET_KEY = 'secret123'  # WEAK SECRET
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 720  # 30 days - too long

# API Configuration
API_BASE_URL = 'https://api.ecommerce.example.com'
API_VERSION = 'v1'  # DEPRECATED VERSION

# Email Configuration - VULNERABILITY: Hardcoded SMTP credentials
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'noreply@ecommerce.example.com'
SMTP_PASSWORD = 'EmailP@ss2023'  # LEAKED EMAIL PASSWORD

# Redis Configuration - VULNERABILITY: No authentication
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_PASSWORD = None  # NO PASSWORD SET

# Security Settings - VULNERABILITY: Debug mode enabled in production
DEBUG = True  # DANGEROUS IN PRODUCTION
SECRET_KEY = 'django-insecure-key-12345'  # WEAK SECRET KEY
ALLOWED_HOSTS = ['*']  # ALLOWS ALL HOSTS

# Session Configuration - VULNERABILITY: Insecure session settings
SESSION_COOKIE_SECURE = False  # SHOULD BE TRUE IN PRODUCTION
SESSION_COOKIE_HTTPONLY = False  # SHOULD BE TRUE
SESSION_COOKIE_SAMESITE = None  # SHOULD BE 'Strict' or 'Lax'

# CORS Configuration - VULNERABILITY: Allows all origins
CORS_ALLOW_ALL_ORIGINS = True  # DANGEROUS
CORS_ALLOW_CREDENTIALS = True

# Logging Configuration - VULNERABILITY: Logs sensitive data
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',  # LOGS EVERYTHING INCLUDING SENSITIVE DATA
        },
    },
}

# Admin Configuration - VULNERABILITY: Default admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'  # DEFAULT PASSWORD
ADMIN_EMAIL = 'admin@ecommerce.example.com'

# Third-party API Keys - VULNERABILITY: Multiple leaked keys
SENDGRID_API_KEY = 'SG.1234567890abcdefghij.klmnopqrstuvwxyz1234567890abcdefghijklmno'
TWILIO_ACCOUNT_SID = 'AC1234567890abcdefghijklmnopqrstuv'
TWILIO_AUTH_TOKEN = 'abcdef1234567890abcdef1234567890'
GOOGLE_MAPS_API_KEY = 'AIzaSyD1234567890abcdefghijklmnopqrstuv'

# Database Connection String - VULNERABILITY: Credentials in URL
DATABASE_URL = 'postgresql://admin:P@ssw0rd123!Admin@prod-db.example.com:5432/ecommerce_prod'

# Encryption Keys - VULNERABILITY: Hardcoded encryption key
ENCRYPTION_KEY = b'1234567890123456'  # 16-byte key - HARDCODED
AES_KEY = 'ThisIsASecretKey123456789012'  # WEAK AND HARDCODED

# Feature Flags
ENABLE_PAYMENT_PROCESSING = True
ENABLE_USER_REGISTRATION = True
ENABLE_ADMIN_API = True  # VULNERABILITY: Admin API exposed

# Rate Limiting - VULNERABILITY: No rate limiting
RATE_LIMIT_ENABLED = False
MAX_REQUESTS_PER_MINUTE = None

# File Upload Configuration - VULNERABILITY: No file type validation
ALLOWED_UPLOAD_EXTENSIONS = ['*']  # ALLOWS ALL FILE TYPES
MAX_UPLOAD_SIZE_MB = 100

# Backup Configuration - VULNERABILITY: Backup credentials exposed
BACKUP_S3_BUCKET = 'ecommerce-backups'
BACKUP_ACCESS_KEY = 'AKIAI44QH8DHBEXAMPLE'
BACKUP_SECRET_KEY = 'je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY'

# SSH Keys - VULNERABILITY: Private key in code
SSH_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN
OPQRSTUVWXYZ1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQR
STUVWXYZ1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV
WXYZ1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
-----END RSA PRIVATE KEY-----"""

# OAuth Configuration - VULNERABILITY: Client secrets exposed
OAUTH_CLIENT_ID = 'ecommerce-app-client-id'
OAUTH_CLIENT_SECRET = 'super-secret-oauth-client-secret-12345'
OAUTH_REDIRECT_URI = 'http://localhost:8000/oauth/callback'  # HTTP not HTTPS

# Monitoring and Analytics
GOOGLE_ANALYTICS_ID = 'UA-123456789-1'
SENTRY_DSN = 'https://1234567890abcdef@sentry.io/1234567'

# Internal API Keys - VULNERABILITY: Internal service credentials
INTERNAL_API_KEY = 'internal-api-key-do-not-share-12345'
MICROSERVICE_AUTH_TOKEN = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkludGVybmFsIFNlcnZpY2UiLCJpYXQiOjE1MTYyMzkwMjJ9.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'

# Legacy Configuration - VULNERABILITY: Old unused settings
LEGACY_API_ENDPOINT = 'http://old-api.example.com/v1'  # DEPRECATED
LEGACY_API_KEY = 'legacy-key-should-be-removed'
OLD_DATABASE_HOST = '10.0.0.50'
OLD_DATABASE_PASSWORD = 'OldP@ssw0rd2020'  # SHOULD BE REMOVED

# Made with Bob
