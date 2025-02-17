def test_get_user_info(test_client):
    """Тест получения информации о пользователе (баланс, инвентарь, история)"""

    # 1. Регистрируем пользователя
    user = test_client.post("/api/auth", json={"username": "test_user", "password": "test_password"}).json
    token = user.get("token")
    assert token, "Ошибка: API не вернул JWT-токен"

    # 2. Запрашиваем информацию о пользователе
    response = test_client.get("/api/info", headers={"Authorization": f"Bearer {token}"})

    # 3. Проверяем статус-код
    assert response.status_code == 200, f"Ошибка: API вернул {response.status_code}, ожидался 200"

    # 4. Проверяем, что в ответе есть ключи coins, inventory, coinHistory
    json_data = response.json
    assert "coins" in json_data, "Ошибка: API не вернул баланс"
    assert "inventory" in json_data, "Ошибка: API не вернул инвентарь"
    assert "coinHistory" in json_data, "Ошибка: API не вернул историю транзакций"
