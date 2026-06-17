from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    otp_token = StringField('Код 2FA')
    remember = BooleanField('Запомнить меня')
    captcha_answer = StringField('Ответ на пример', validators=[DataRequired()])

class ContactForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Сообщение', validators=[DataRequired()])
    captcha_answer = StringField('Ответ на пример', validators=[DataRequired()])

class AutoSchoolForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    phone = StringField('Телефон', validators=[DataRequired()])
    category = SelectField('Категория', choices=[('B (МКПП)', 'B (МКПП)'), ('B (АКПП)', 'B (АКПП)'), ('A', 'A')])
    agree = BooleanField('Согласие на обработку ПД', validators=[DataRequired()])
    captcha_answer = StringField('Ответ на пример', validators=[DataRequired()])