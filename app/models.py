from .extensions import db

class User(db.Model):
    """
    Модель пользователя (сотрудника).
    - id: уникальный идентификатор.
    - username: логин (уникальный, не может быть пустым).
    - password: пароль (не может быть пустым).
    - balance: баланс монет (по умолчанию 1000, не может быть отрицательным).
    """
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    balance = db.Column(db.Integer, default=1000, nullable=False)

    # Ограничение: баланс не может быть меньше 0
    __table_args__ = (
        db.CheckConstraint("balance >= 0", name="non_negative_balance"),
    )

    def transfer_coins(self, receiver, amount):
        """Перевод монеты"""
        if amount <= 0:
            return False
        if self.balance < amount:
            return False
        if receiver is None or receiver.id == self.id:
            return False

        self.balance -= amount
        receiver.balance += amount

        return True

    def buy_item(self, item):
        """Покупка товара"""
        if item is None or item.price <= 0:
            return False
        if self.balance < item.price:
            return False

        self.balance -= item.price

        return True

class Merch(db.Model):
    """
    Модель товара (мерча).
    - id: уникальный идентификатор.
    - name: название товара (уникальное, не может быть пустым).
    - price: цена в монетах.
    """
    __tablename__ = "merch"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)

class Transaction(db.Model):
    """
    Модель транзакции (перевод монет между пользователями).
    - id: уникальный идентификатор.
    - sender_id: ID отправителя (внешний ключ к User).
    - receiver_id: ID получателя (внешний ключ к User).
    - amount: сумма перевода.
    - timestamp: время создания транзакции (автоматически заполняется).
    """
    __tablename__ = "transaction"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    sender = db.relationship("User", foreign_keys=[sender_id], backref="sent_transactions")
    receiver = db.relationship("User", foreign_keys=[receiver_id], backref="received_transactions")

class Purchase(db.Model):
    """
    Модель покупки товара.
    - id: уникальный идентификатор.
    - user_id: ID пользователя (внешний ключ к User).
    - merch_id: ID товара (внешний ключ к Merch).
    - timestamp: время покупки (автоматически заполняется).
    """
    __tablename__ = "purchase"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    merch_id = db.Column(db.Integer, db.ForeignKey("merch.id"), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", backref="purchases")
    merch = db.relationship("Merch", backref="purchases")