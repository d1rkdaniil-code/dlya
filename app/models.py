from app.extensions import db
from flask_login import UserMixin
from app.utils import fernet

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    otp_secret_encrypted = db.Column(db.LargeBinary, nullable=False)
    is_2fa_enabled = db.Column(db.Boolean, default=False)

    def set_otp_secret(self, secret):
        self.otp_secret_encrypted = fernet.encrypt(secret.encode())

    def get_otp_secret(self):
        return fernet.decrypt(self.otp_secret_encrypted).decode()

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_read = db.Column(db.Boolean, default=False)

class AutoSchoolApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_processed = db.Column(db.Boolean, default=False)