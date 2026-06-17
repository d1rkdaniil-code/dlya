from flask import Blueprint, jsonify
from app.utils import PRODUCTS

api_bp = Blueprint('api', __name__)

@api_bp.route('/projects')
def list_projects():
    return jsonify([
        {"id": 1, "name": "Автошкола", "url": "/project/auto-school"},
        {"id": 2, "name": "Магазин-бот", "url": "/project/shop-bot"},
        {"id": 3, "name": "Парсер HH.ru", "url": "/project/hh-parser"},
    ])

@api_bp.route('/products')
def list_products():
    return jsonify(PRODUCTS)