from app.models import User, Merch, Transaction, Purchase

def test_user_creation():
    from app.models import User
    user = User(username="test", password="secret")
    assert user.balance == 1000  # Теперь баланс будет 1000
    assert user.username == "test"

def test_merch_creation():
    merch = Merch(name="t-shirt", price=80)
    assert merch.name == "t-shirt"
    assert merch.price == 80

def test_transaction_creation():
    transaction = Transaction(sender_id=1, receiver_id=2, amount=100)
    assert transaction.amount == 100