from flask import Blueprint, render_template
from app.forms import ContactForm
from app.models import ContactMessage
from app.utils import send_email, generate_captcha, check_captcha
from app.extensions import db, limiter
from flask import request, flash, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def contact():
    form = ContactForm()
    if request.method == 'GET':
        a, b = generate_captcha()
        return render_template('contact.html', form=form, captcha_a=a, captcha_b=b)
    if form.validate_on_submit():
        if not check_captcha(request.form.get('captcha_answer', '')):
            flash('Неверный ответ на проверочный вопрос.', 'danger')
            a, b = generate_captcha()
            return render_template('contact.html', form=form, captcha_a=a, captcha_b=b)
        msg = ContactMessage(name=form.name.data, email=form.email.data, message=form.message.data)
        db.session.add(msg)
        db.session.commit()
        send_email(f'Новое сообщение от {form.name.data}',
                   f'Имя: {form.name.data}\nEmail: {form.email.data}\n\n{form.message.data}')
        flash('Сообщение отправлено! Я свяжусь с вами.', 'success')
        return redirect(url_for('main.contact'))
    a, b = generate_captcha()
    return render_template('contact.html', form=form, captcha_a=a, captcha_b=b)

@main_bp.route('/projects')
def projects():
    return render_template('projects.html')