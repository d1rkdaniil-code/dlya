import os
from flask import Flask
from app.config import config_dict
from app.extensions import db, login_manager, csrf, limiter, talisman, migrate, cache
from app.utils import fernet

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])

    if app.config['SECRET_KEY'] == 'dev-secret-key-change-me-immediately':
        raise RuntimeError("SECRET_KEY must be set in environment")
    if config_name == 'production' and app.config['ADMIN_PASSWORD'] == 'change-me-immediately':
        raise RuntimeError("ADMIN_PASSWORD must be changed in production")

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)

    talisman.init_app(
        app,
        force_https=config_name == 'production',
        content_security_policy=None,
        session_cookie_secure=config_name == 'production',
    )

    from app.blueprints.main import main_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.projects import projects_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.api import api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(projects_bp, url_prefix='/project')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        from app import models
        db.create_all()
        if not models.User.query.filter_by(username=app.config['ADMIN_USERNAME']).first():
            import pyotp
            from werkzeug.security import generate_password_hash
            raw_secret = pyotp.random_base32()
            admin = models.User(
                username=app.config['ADMIN_USERNAME'],
                password_hash=generate_password_hash(app.config['ADMIN_PASSWORD']),
                is_2fa_enabled=False
            )
            admin.set_otp_secret(raw_secret)
            db.session.add(admin)
            db.session.commit()

    return app