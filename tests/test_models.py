from app.models import User, Merch, Transaction


def test_user_creation():
    user = User(username="test", password="secret")

    assert user.username == "test"
    assert user.password == "secret"


def test_merch_creation():
    merch = Merch(name="t-shirt", price=80)

    assert merch.name == "t-shirt"
    assert merch.price == 80


def test_transaction_creation():
    transaction = Transaction(sender_id=1, receiver_id=2, amount=100)

    assert transaction.sender_id == 1
    assert transaction.receiver_id == 2
    assert transaction.amount == 100


def test_transfer_coins():
    sender = User(id=1, username="sender", balance=100)
    receiver = User(id=2, username="receiver", balance=50)

    assert sender.transfer_coins(receiver, 30) is True, "Ошибка: перевод должен быть успешным"
    assert sender.balance == 70, "Ошибка: баланс отправителя должен уменьшиться"
    assert receiver.balance == 80, "Ошибка: баланс получателя должен увеличиться"


def test_transfer_coins_not_enough_money():
    sender = User(id=1, username="sender", balance=50)
    receiver = User(id=2, username="receiver", balance=50)

    assert sender.transfer_coins(receiver, 100) is False, "Ошибка: нельзя перевести больше, чем есть на балансе"
    assert sender.balance == 50, "Ошибка: баланс не должен измениться после неуспешного перевода"


def test_transfer_coins_to_myself():
    sender = User(id=1, username="sender", balance=100)

    assert sender.transfer_coins(sender, 10) is False, "Ошибка: нельзя перевести деньги самому себе"
    assert sender.balance == 100, "Ошибка: баланс не должен измениться после попытки перевода самому себе"


def test_buy_item():
    user = User(id=1, username="buyer", balance=100)
    item = Merch(id=1, name="cup", price=50)

    assert user.buy_item(item) is True, "Ошибка: покупка должна быть успешной"
    assert user.balance == 50, "Ошибка: баланс пользователя должен уменьшиться после покупки"


def test_buy_item_not_enough_money_to_buy():
    user = User(id=1, username="buyer", balance=100)
    item = Merch(id=1, name="book", price=150)

    assert user.buy_item(item) is False, "Ошибка: нельзя купить товар без достаточного количества монет"
    assert user.balance == 100, "Ошибка: баланс не должен измениться после неуспешной покупки"
