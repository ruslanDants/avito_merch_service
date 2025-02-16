from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token

from .extensions import db, jwt
from .models import User


auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    # Проверка наличия обязательных полей
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400

    # Проверка уникальности логина
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    # Создание пользователя
    user = User(username=data['username'], password=data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created'}), 201

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Проверка наличия обязательных полей
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Поиск пользователя в базе
    user = User.query.filter_by(username=username).first()
    if not user or user.password != password:
        return jsonify({"error": "Invalid credentials"}), 401

    # Генерация токена
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200