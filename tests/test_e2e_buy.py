def test_e2e_buy_merch(test_client, faker):
    """E2E-тест: пользователь покупает товар и проверяет инвентарь"""

    username = faker.user_name()
    password = faker.password()

    # 1. Регистрация и логин
    auth_response = test_client.post("/api/auth", json={
        "username": username,
        "password": password
    }).get_json()

    token = auth_response["token"]

    # 2. Получаем начальный баланс и инвентарь
    user_info = test_client.get("/api/info", headers={
        "Authorization": f"Bearer {token}"
    }).get_json()

    initial_balance = user_info.get("coins", 0)
    inventory_before = user_info.get("inventory", [])

    # 3. Покупаем товар "t-shirt"
    item_name = "t-shirt"
    buy_response = test_client.get(f"/api/buy/{item_name}", headers={
        "Authorization": f"Bearer {token}"
    })

    assert buy_response.status_code == 200, f"Ошибка: {buy_response.get_json()}"

    # 4. Проверяем, что баланс уменьшился
    new_user_info = test_client.get("/api/info", headers={
        "Authorization": f"Bearer {token}"
    }).get_json()

    new_balance = new_user_info.get("coins", 0)
    assert new_balance == initial_balance - 80, "Ошибка: баланс пользователя неверно уменьшился"

    # 5. Проверяем, что товар добавлен в `inventory`
    inventory_after = new_user_info.get("inventory", [])
    assert len(inventory_after) == len(inventory_before) + 1, "Ошибка: товар не добавлен в инвентарь"

    last_item = inventory_after[-1]
    assert last_item["type"] == item_name, f"Ошибка: в инвентаре нет '{item_name}'"
    assert last_item["quantity"] == 1, "Ошибка: неверное количество товара в инвентаре"
