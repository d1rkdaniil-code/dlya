import os
import time
import random
import requests
import logging
from flask import session, current_app
from cryptography.fernet import Fernet
from app.extensions import cache

logger = logging.getLogger(__name__)

fernet = Fernet(os.getenv('FERNET_KEY', Fernet.generate_key().decode()).encode())

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
]

PRODUCTS = {
    1: {'name': 'Смартфон X', 'price': 29990},
    2: {'name': 'Наушники Pro', 'price': 4990},
    3: {'name': 'Чехол-книжка', 'price': 990},
}

def make_request(url, params=None, method='GET'):
    max_retries = 3
    retries = 0
    delay = 1.0
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9',
        'Referer': 'https://hh.ru/',
    }
    while retries <= max_retries:
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=15)
            else:
                response = requests.post(url, data=params, headers=headers, timeout=15)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                logger.warning(f"Rate limited, retry {retries+1}/{max_retries}")
                time.sleep(delay * 2)
            elif response.status_code in (500, 502, 503, 504):
                logger.warning(f"Server error {response.status_code}, retry {retries+1}/{max_retries}")
            else:
                logger.error(f"Request failed with status {response.status_code}")
                return None
        except Exception as e:
            logger.warning(f"Network error: {e}, retry {retries+1}/{max_retries}")
        if retries == max_retries:
            return None
        time.sleep(delay)
        delay *= 2
        retries += 1
    return None

def _extract_vacancies(items, result_list):
    for item in items:
        salary_info = item.get('salary')
        salary_text = 'Не указана'
        if salary_info:
            frm = salary_info.get('from')
            to = salary_info.get('to')
            cur = salary_info.get('currency', '')
            if frm and to:
                salary_text = f"{frm} - {to} {cur}"
            elif frm:
                salary_text = f"от {frm} {cur}"
            elif to:
                salary_text = f"до {to} {cur}"
        result_list.append({
            'title': item.get('name', 'Не указано'),
            'company': item.get('employer', {}).get('name', 'Не указано'),
            'salary': salary_text,
            'link': item.get('alternate_url', '#'),
            'date': (item.get('published_at', '') or '')[:10] or 'Не указана'
        })

@cache.memoize(timeout=600)
def parse_hh_cached(query, max_pages=2):
    return parse_hh(query, max_pages)

def parse_hh(query, max_pages=2):
    if not query or not query.strip():
        return []
    all_vacancies = []
    api_url = "https://api.hh.ru/vacancies"
    params = {
        "text": query,
        "per_page": 20,
        "page": 0,
        "area": 1,
        "only_with_salary": False,
        "order_by": "relevance",
    }
    try:
        response = make_request(api_url, params)
        if not response:
            return []
        data = response.json()
        items = data.get('items', [])
        _extract_vacancies(items, all_vacancies)
        pages = min(data.get('pages', 0), max_pages)
        for p in range(1, pages):
            time.sleep(0.3 + random.random() * 0.2)
            params['page'] = p
            resp = make_request(api_url, params)
            if resp:
                _extract_vacancies(resp.json().get('items', []), all_vacancies)
            else:
                break
        return all_vacancies
    except Exception as e:
        logger.error(f"HH API error: {e}")
        return []

def send_email(subject, body, to=None):
    if to is None:
        to = current_app.config['TO_EMAIL']
    try:
        import smtplib
        from email.message import EmailMessage
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = current_app.config['SMTP_LOGIN']
        msg['To'] = to
        msg.set_content(body)
        with smtplib.SMTP_SSL(current_app.config['SMTP_SERVER'], current_app.config['SMTP_PORT']) as smtp:
            smtp.login(current_app.config['SMTP_LOGIN'], current_app.config['SMTP_PASSWORD'])
            smtp.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Email error (credentials hidden): {str(e).replace(current_app.config['SMTP_PASSWORD'], '***')}")
        return False

def generate_captcha():
    a = random.randint(1, 15)
    b = random.randint(1, 15)
    session['captcha_result'] = a + b
    return a, b

def check_captcha(answer):
    try:
        return int(answer) == session.pop('captcha_result', None)
    except (ValueError, TypeError):
        return False