from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user, login_user
from app.extensions import db, limiter
from app.models import User, ContactMessage, AutoSchoolApplication
from app.forms import LoginForm
from app.utils import generate_captcha, check_captcha
import pyotp
from werkzeug.security import check_password_hash
import time
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    form = LoginForm()
    if request.method == 'GET':
        a, b = generate_captcha()
        return render_template('admin_login.html', form=form, captcha_a=a, captcha_b=b)
    if form.validate_on_submit():
        if not check_captcha(request.form.get('captcha_answer', '')):
            flash('Неверный ответ на проверочный вопрос.', 'danger')
            a, b = generate_captcha()
            return render_template('admin_login.html', form=form, captcha_a=a, captcha_b=b)
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            if user.is_2fa_enabled:
                token = form.otp_token.data or ''
                totp = pyotp.TOTP(user.get_otp_secret())
                if not totp.verify(token):
                    flash('Неверный код 2FA', 'danger')
                    a, b = generate_captcha()
                    return render_template('admin_login.html', form=form, captcha_a=a, captcha_b=b)
            login_user(user, remember=form.remember.data)
            flash('Вход выполнен', 'success')
            return redirect(url_for('admin.dashboard'))
        logger.warning(f"Failed login attempt for user '{form.username.data}' from IP {request.remote_addr}")
        time.sleep(2)
        flash('Неверный логин или пароль', 'danger')
    a, b = generate_captcha()
    return render_template('admin_login.html', form=form, captcha_a=a, captcha_b=b)

@admin_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Выход выполнен', 'success')
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@login_required
def dashboard():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    applications = AutoSchoolApplication.query.order_by(AutoSchoolApplication.created_at.desc()).all()
    return render_template('admin_dashboard.html', messages=messages, applications=applications)

@admin_bp.route('/message/<int:id>/read', methods=['POST'])
@login_required
def mark_message_read(id):
    msg = ContactMessage.query.get_or_404(id)
    msg.is_read = True
    db.session.commit()
    flash('Сообщение отмечено прочитанным', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/application/<int:id>/process', methods=['POST'])
@login_required
def mark_application_processed(id):
    app_item = AutoSchoolApplication.query.get_or_404(id)
    app_item.is_processed = True
    db.session.commit()
    flash('Заявка отмечена обработанной', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/setup-2fa')
@login_required
def setup_2fa():
    if current_user.is_2fa_enabled:
        flash('2FA уже включена', 'info')
        return redirect(url_for('admin.dashboard'))
    totp = pyotp.TOTP(current_user.get_otp_secret())
    uri = totp.provisioning_uri(current_user.username, issuer_name='Portfolio')
    qr_url = f'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={uri}'
    return render_template('setup_2fa.html', qr_url=qr_url, secret=current_user.get_otp_secret())

@admin_bp.route('/enable-2fa', methods=['POST'])
@login_required
def enable_2fa():
    token = request.form.get('token')
    if not token:
        flash('Введите код из приложения', 'danger')
        return redirect(url_for('admin.setup_2fa'))
    totp = pyotp.TOTP(current_user.get_otp_secret())
    if totp.verify(token):
        current_user.is_2fa_enabled = True
        db.session.commit()
        flash('2FA успешно включена', 'success')
    else:
        flash('Неверный код', 'danger')
    return redirect(url_for('admin.dashboard'))