from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import db, User, Merch, Transaction, Purchase

api_bp = Blueprint("api", __name__, url_prefix="/api")


# Аутентификация или регистрация
@api_bp.route("/auth", methods=["POST"])
def auth():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Проверка обязательных полей
    if not username or not password:
        return jsonify({"errors": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()

    # Если пользователь не существует - создаем нового
    if not user:
        try:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"errors": "Registration failed"}), 500
    else:
        # Проверяем пароль существующего пользователя
        if user.password != password:
            return jsonify({"errors": "Invalid credentials"}), 401

    # Генерация токена
    access_token = create_access_token(identity=str(user.id))
    return jsonify({"token": access_token}), 200


# Информация о пользователе
@api_bp.route("/info", methods=["GET"])
@jwt_required()
def info():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"errors": "User not found"}), 404

    # Инвентарь
    purchases = Purchase.query.filter_by(user_id=user_id).all()
    inventory = {}
    for purchase in purchases:
        item_name = purchase.merch.name
        inventory[item_name] = inventory.get(item_name, 0) + 1

    inventory_list = [
        {"type": name, "quantity": count}
        for name, count in inventory.items()
    ]

    # История переводов
    sent = Transaction.query.filter_by(sender_id=user_id).all()
    received = Transaction.query.filter_by(receiver_id=user_id).all()

    coin_history = {
        "received": [
            {"fromUser": t.sender.username, "amount": t.amount}
            for t in received
        ],
        "sent": [
            {"toUser": t.receiver.username, "amount": t.amount}
            for t in sent
        ]
    }

    return jsonify({
        "coins": user.balance,
        "inventory": inventory_list,
        "coinHistory": coin_history
    }), 200


# Перевод монет
@api_bp.route("/sendCoin", methods=["POST"])
@jwt_required()
def send_coin():
    data = request.get_json()
    sender_id = int(get_jwt_identity())

    # Проверка наличия всех полей
    if not data or "toUser" not in data or "amount" not in data:
        return jsonify({"errors": "Missing required fields"}), 400

    # Проверка типа данных
    try:
        amount = int(data["amount"])
    except ValueError:
        return jsonify({"errors": "Amount must be an integer"}), 400

    # Проверка валидности суммы
    if amount <= 0:
        return jsonify({"errors": "Amount must be positive"}), 400

    # Поиск получателя
    receiver = User.query.filter_by(username=data["toUser"]).first()
    if not receiver:
        return jsonify({"errors": "Receiver not found"}), 404

    # Проверка отправителя
    sender = db.session.get(User, sender_id)
    if not sender:
        return jsonify({"errors": "Sender not found"}), 404

    # Выполнение перевода
    if not sender.transfer_coins(receiver, amount):
        return jsonify({"errors": "Insufficient funds or invalid transaction"}), 400

    try:
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
        return jsonify({"errors": str(e)}), 500


# Покупка товара
@api_bp.route("/buy/<string:item>", methods=["GET"])
@jwt_required()
def buy(item):
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    merch = Merch.query.filter_by(name=item).first()

    if not merch:
        return jsonify({"errors": "Item not found"}), 404

    # Покупка товара
    if not user.buy_item(merch):
        return jsonify({"errors": "Insufficient funds"}), 400

    try:
        purchase = Purchase(user_id=user_id, merch_id=merch.id)
        db.session.add(purchase)
        db.session.commit()
        return jsonify({"message": "Purchase successful"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": str(e)}), 500