def test_e2e_transfer_coins(test_client, faker):
    """E2E-тест: отправка монет от одного пользователя другому"""

    # Генерируем случайные имена
    sender_name = faker.user_name()
    receiver_name = faker.user_name()

    # 1. Создаем двух пользователей
    sender = test_client.post("/api/auth", json={"username": sender_name, "password": "1234"}).get_json()
    receiver = test_client.post("/api/auth", json={"username": receiver_name, "password": "5678"}).get_json()

    sender_token = sender["token"]

    # 2. Получаем начальный баланс и историю отправителя
    sender_info = test_client.get("/api/info", headers={"Authorization": f"Bearer {sender_token}"}).get_json()
    sender_balance = sender_info.get("coins", 0)
    sender_sent_before = sender_info.get("coinHistory", {}).get("sent", [])

    # 3. Получаем начальный баланс и историю получателя
    receiver_info = test_client.get("/api/info", headers={"Authorization": f"Bearer {receiver['token']}"}).get_json()
    receiver_balance = receiver_info.get("coins", 0)
    receiver_received_before = receiver_info.get("coinHistory", {}).get("received", [])

    # 4. Отправляем 50 монет
    transfer_response = test_client.post("/api/sendCoin", json={
        "toUser": receiver_name,
        "amount": 50
    }, headers={"Authorization": f"Bearer {sender_token}"})

    assert transfer_response.status_code == 200, f"Ошибка: {transfer_response.get_json()}"

    # 5. Проверяем баланс отправителя
    new_sender_info = test_client.get("/api/info", headers={"Authorization": f"Bearer {sender_token}"}).get_json()
    new_sender_balance = new_sender_info.get("coins", 0)
    sender_sent_after = new_sender_info.get("coinHistory", {}).get("sent", [])

    assert new_sender_balance == sender_balance - 50, "Ошибка: баланс отправителя неверно уменьшился"
    assert len(sender_sent_after) == len(sender_sent_before) + 1, "Ошибка: запись о переводе не добавлена"

    last_sent = sender_sent_after[-1]
    assert last_sent["amount"] == 50, "Ошибка: сумма перевода неверная"
    assert last_sent["toUser"] == receiver_name, f"Ошибка: перевод ушел не тому пользователю {receiver_name}"

    # 6. Проверяем баланс получателя
    new_receiver_info = test_client.get("/api/info", headers={"Authorization": f"Bearer {receiver['token']}"}).get_json()
    new_receiver_balance = new_receiver_info.get("coins", 0)
    receiver_received_after = new_receiver_info.get("coinHistory", {}).get("received", [])

    assert new_receiver_balance == receiver_balance + 50, "Ошибка: баланс получателя неверно увеличился"
    assert len(receiver_received_after) == len(receiver_received_before) + 1, "Ошибка: запись о получении монет не добавлена"

    last_received = receiver_received_after[-1]
    assert last_received["amount"] == 50, "Ошибка: сумма полученных монет неверная"
    assert last_received["fromUser"] == sender_name, f"Ошибка: перевод пришел не от {sender_name}"
