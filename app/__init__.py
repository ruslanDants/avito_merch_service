from flask import Flask
from .extensions import db, jwt


def create_app():
    # Создаем экземпляр приложения
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:password@db:5432/merch_db"
    app.config["JWT_SECRET_KEY"] = "super-secret-key"  # Замените на случайный ключ в реальном проекте!

    # Инициализация расширений
    db.init_app(app)
    jwt.init_app(app)

    # Создание таблиц и заполнение товаров
    with app.app_context():
        from .models import User, Merch
        db.create_all()
        # Добавление товаров, если таблица пуста
        if db.session.query(db.exists().where(Merch.id == 1)).scalar():
            return  # Товары уже добавлены
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

    # Импорт и регистрация маршрутов
    from .routes import auth_bp, api_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp)

    return app