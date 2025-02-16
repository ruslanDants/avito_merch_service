from flask import Flask
from sqlalchemy import inspect

from .extensions import db, jwt


def create_app():
    # Создаем экземпляр приложения
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@db:5432/merch_db"
    app.config["JWT_SECRET_KEY"] = "super-secret-key"

    # Инициализация расширений
    db.init_app(app)
    jwt.init_app(app)

    # Создание таблиц и заполнение товаров
    with app.app_context():
        from .models import Merch
        inspector = inspect(db.engine)
        if not inspector.has_table("user"):
            print("Initialize data")
            db.create_all()
            merch_items = [
                {"name": "t-shirt", "price": 80},
                {"name": "cup", "price": 20},
                {"name": "book", "price": 50},
                {"name": "pen", "price": 10},
                {"name": "powerbank", "price": 200},
                {"name": "hoody", "price": 300},
                {"name": "umbrella", "price": 200},
                {"name": "socks", "price": 10},
                {"name": "wallet", "price": 50},
                {"name": "pink-hoody", "price": 500},
            ]
            for item in merch_items:
                db.session.add(Merch(**item))
            db.session.commit()

        # Выполнить миграции
        with open("migrations/001_create_indexes.sql") as f:
            sql = f.read()
            db.session.execute(sql)
            db.session.commit()

    # Импорт и регистрация маршрутов
    from .routes import api_bp
    app.register_blueprint(api_bp)

    return app