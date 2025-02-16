from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from .extensions import db, jwt
from .models import User, Merch, Purchase, Transaction

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/register', methods=['POST'])
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


@auth_bp.route('/login', methods=['POST'])
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
    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "balance": user.balance
    }), 200


api_bp = Blueprint("api", __name__)

@api_bp.route('/purchase', methods=['POST'])
@jwt_required()
def purchase():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    data = request.get_json()
    merch_name = data.get("merch_name")
    merch = Merch.query.filter_by(name=merch_name).first()

    if not merch:
        return jsonify({"error": "Merch not found"}), 404

    if user.balance < merch.price:
        return jsonify({"error": "Insufficient funds"}), 400

    try:
        user.balance -= merch.price
        purchase = Purchase(user_id=user.id, merch_id=merch.id)
        db.session.add(purchase)
        db.session.commit()
        return jsonify({"message": "Purchase successful"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@api_bp.route('/history', methods=['GET'])
@jwt_required()
def history():
    user_id = int(get_jwt_identity())  # Получаем ID пользователя из токена

    # Получаем покупки
    purchases = Purchase.query.filter_by(user_id=user_id).all()
    purchases_data = [
        {
            "merch_name": purchase.merch.name,
            "price": purchase.merch.price,
            "timestamp": purchase.timestamp.isoformat()
        } for purchase in purchases
    ]

    # Получаем транзакции
    sent_transactions = Transaction.query.filter_by(sender_id=user_id).all()
    received_transactions = Transaction.query.filter_by(receiver_id=user_id).all()

    transactions_data = []
    for transaction in sent_transactions:
        transactions_data.append({
            "type": "sent",
            "receiver": User.query.get(transaction.receiver_id).username,
            "amount": transaction.amount,
            "timestamp": transaction.timestamp.isoformat()
        })

    for transaction in received_transactions:
        transactions_data.append({
            "type": "received",
            "sender": User.query.get(transaction.sender_id).username,
            "amount": transaction.amount,
            "timestamp": transaction.timestamp.isoformat()
        })

    return jsonify({
        "purchases": purchases_data,
        "transactions": transactions_data
    }), 200


@api_bp.route('/merch', methods=['GET'])
@jwt_required()
def get_all_merch():
    merch_items = Merch.query.all()

    merch_list = [
        {
            "id": item.id,
            "name": item.name,
            "price": item.price
        } for item in merch_items
    ]

    return jsonify(merch_list), 200


@api_bp.route('/merch/<int:merch_id>', methods=['GET'])
@jwt_required()
def get_merch(merch_id):
    merch = Merch.query.get(merch_id)

    if not merch:
        return jsonify({"error": "Merch not found"}), 404

    return jsonify({
        "id": merch.id,
        "name": merch.name,
        "price": merch.price
    }), 200


@api_bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer():
    sender_id = int(get_jwt_identity())  # ID отправителя из токена
    data = request.get_json()

    # Проверка обязательных полей
    receiver_username = data.get("receiver")
    amount = data.get("amount")
    if not receiver_username or not amount:
        return jsonify({"error": "Receiver username and amount are required"}), 400

    # Проверка суммы
    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400

    # Поиск получателя
    receiver = User.query.filter_by(username=receiver_username).first()
    if not receiver:
        return jsonify({"error": "Receiver not found"}), 404

    # Проверка, что отправитель != получателю
    if sender_id == receiver.id:
        return jsonify({"error": "You cannot transfer to yourself"}), 400

    # Получение объекта отправителя
    sender = User.query.get(sender_id)
    if not sender:
        return jsonify({"error": "Sender not found"}), 404

    # Проверка баланса отправителя
    if sender.balance < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    # Выполнение перевода
    try:
        sender.balance -= amount
        receiver.balance += amount

        # Создание записи о транзакции
        transaction = Transaction(
            sender_id=sender_id,
            receiver_id=receiver.id,
            amount=amount
        )
        db.session.add(transaction)
        db.session.commit()

        return jsonify({"message": "Transfer successful"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500