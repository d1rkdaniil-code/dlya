import os
from datetime import timedelta

class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me-immediately')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(days=30)

    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.yandex.ru')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 465))
    SMTP_LOGIN = os.getenv('SMTP_LOGIN', 'your@email.com')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'your-password')
    TO_EMAIL = os.getenv('TO_EMAIL', 'your@email.com')

    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'change-me-immediately')

    RATELIMIT_STORAGE_URI = os.getenv('RATELIMIT_STORAGE_URI', 'memory://')
    FERNET_KEY = os.getenv('FERNET_KEY', '')
    if not FERNET_KEY:
        from cryptography.fernet import Fernet
        FERNET_KEY = Fernet.generate_key().decode()
        os.environ['FERNET_KEY'] = FERNET_KEY

    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False

config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}