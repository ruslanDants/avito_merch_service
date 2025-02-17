def test_register_user(test_client, faker):
    """Тест регистрации нового пользователя"""

    username = faker.user_name()
    password = faker.password()

    # 1. Регистрируем пользователя и получаем токен
    response = test_client.post("/api/auth", json={
        "username": username,
        "password": password
    })

    assert response.status_code == 200  # API возвращает 200, а не 201
    json_data = response.json

    # 2. Проверяем, что API вернул токен
    assert "token" in json_data, "Ошибка: API не вернул JWT-токен"

    # 3. Проверяем, что токен - строка
    assert isinstance(json_data["token"], str), "Ошибка: токен должен быть строкой"
