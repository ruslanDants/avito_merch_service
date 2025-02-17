import pytest
from faker import Faker
from app import create_app
from app.extensions import db

@pytest.fixture(scope="module")
def test_client():
    """Создает клиент для тестирования API"""
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as testing_client:
        with app.app_context():
            db.session.begin_nested()  # Начинаем транзакцию
        yield testing_client  # Передаем клиент в тесты
        with app.app_context():
            db.session.rollback()  # Откатываем изменения после тестов

@pytest.fixture
def faker():
    """Создает экземпляр Faker"""
    return Faker()