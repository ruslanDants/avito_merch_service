def test_buy_item(test_client):
    """Тест покупки предмета"""

    # 1. Логинимся
    auth_response = test_client.post("/api/auth", json={
        "username": "test_user",
        "password": "test_password"
    }).get_json()

    token = auth_response["token"]

    # 2. Покупаем "book"
    response = test_client.get("/api/buy/book", headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 200, f"Ошибка: {response.get_json()}"
