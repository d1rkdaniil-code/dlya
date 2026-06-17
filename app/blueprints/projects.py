import io
import csv
from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, session, Response)
from app.forms import AutoSchoolForm
from app.models import AutoSchoolApplication
from app.utils import (PRODUCTS, send_email, parse_hh_cached,
                       generate_captcha, check_captcha)
from app.extensions import db, limiter

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/auto-school', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def auto_school():
    form = AutoSchoolForm()
    if request.method == 'GET':
        a, b = generate_captcha()
        return render_template('project_auto_school.html', form=form, captcha_a=a, captcha_b=b)
    if form.validate_on_submit():
        if not check_captcha(request.form.get('captcha_answer', '')):
            flash('Неверный ответ на проверочный вопрос.', 'danger')
            a, b = generate_captcha()
            return render_template('project_auto_school.html', form=form, captcha_a=a, captcha_b=b)
        application = AutoSchoolApplication(
            name=form.name.data, phone=form.phone.data, category=form.category.data
        )
        db.session.add(application)
        db.session.commit()
        send_email('Новая заявка в автошколу',
                   f'Имя: {form.name.data}\nТелефон: {form.phone.data}\nКатегория: {form.category.data}')
        flash('Заявка успешно отправлена! Мы свяжемся с вами.', 'success')
        return redirect(url_for('projects.auto_school'))
    a, b = generate_captcha()
    return render_template('project_auto_school.html', form=form, captcha_a=a, captcha_b=b)

@projects_bp.route('/shop-bot')
def shop_bot():
    products_with_id = [{'id': id, **data} for id, data in PRODUCTS.items()]
    cart = session.get('cart', {})
    cart_count = sum(cart.values())
    return render_template('project_shop_bot.html', products=products_with_id, cart_count=cart_count)

@projects_bp.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if product_id not in PRODUCTS:
        flash('Товар не найден', 'danger')
        return redirect(url_for('projects.shop_bot'))
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    flash(f'Товар «{PRODUCTS[product_id]["name"]}» добавлен в корзину', 'success')
    return redirect(url_for('projects.shop_bot'))

@projects_bp.route('/cart')
def show_cart():
    cart = session.get('cart', {})
    items = []
    total = 0
    for pid, qty in cart.items():
        product = PRODUCTS.get(int(pid))
        if product:
            items.append({'id': pid, 'name': product['name'], 'price': product['price'], 'qty': qty})
            total += product['price'] * qty
    return render_template('cart.html', items=items, total=total)

@projects_bp.route('/remove-from-cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        session['cart'] = cart
        flash('Товар удалён из корзины', 'success')
    return redirect(url_for('projects.show_cart'))

@projects_bp.route('/clear-cart', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    flash('Корзина очищена', 'success')
    return redirect(url_for('projects.show_cart'))

@projects_bp.route('/hh-parser', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def hh_parser():
    vacancies = []
    query = ''
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            session.pop('_flashes', None)
            vacancies = parse_hh_cached(query, max_pages=2)
            if not vacancies:
                flash('Не удалось найти вакансии. Попробуйте другой запрос.', 'danger')
        else:
            flash('Введите запрос для поиска', 'danger')
    return render_template('project_hh_parser.html', vacancies=vacancies, query=query)

@projects_bp.route('/export-csv')
@limiter.limit("3 per minute")
def export_csv():
    query = request.args.get('query', '')
    if not query:
        flash('Не указан запрос', 'danger')
        return redirect(url_for('projects.hh_parser'))
    vacancies = parse_hh_cached(query, max_pages=2)
    if not vacancies:
        flash('Нет данных для экспорта', 'danger')
        return redirect(url_for('projects.hh_parser'))
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Название', 'Компания', 'Зарплата', 'Дата', 'Ссылка'])
    for v in vacancies:
        writer.writerow([v['title'], v['company'], v['salary'], v['date'], v['link']])
    output.seek(0)
    return Response(output, mimetype='text/csv',
                    headers={'Content-Disposition': f'attachment; filename=hh_vacancies_{query}.csv'})