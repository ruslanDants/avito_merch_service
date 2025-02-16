# Сервис магазина мерча для сотрудников Авито

**Описание**:  
Микросервис для управления виртуальными монетами сотрудников, покупки мерча и отслеживания транзакций. Реализовано:
- 🔐 JWT-авторизация
- 💸 Перевод монет между сотрудниками
- 🛒 Покупка мерча из каталога
- 📊 История операций (входящие/исходящие транзакции)

## 🛠 Технологии
- **Язык**: Python 3.10
- **База данных**: PostgreSQL + SQLAlchemy (ORM)
- **Тестирование**: Pytest (unit + E2E)
- **Деплой**: Docker Compose

## 🚀 Запуск
1. Команда:
   ```bash
   docker-compose up --build