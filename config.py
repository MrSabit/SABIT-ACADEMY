import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or os.environ.get('MAIL_USERNAME')
    
    # Production vs Development detection
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        # Development mode
        MAIL_SUPPRESS_SEND = True
        MAIL_DEFAULT_SENDER = 'noreply@example.com'
        SERVER_NAME = os.environ.get('SERVER_NAME') or 'localhost:5000'
        PREFERRED_URL_SCHEME = 'http'
    else:
        # Production mode - email is configured
        SERVER_NAME = os.environ.get('SERVER_NAME')
        PREFERRED_URL_SCHEME = 'https'