def test_login_page(client):
    response = client.get('/admin/login')
    assert response.status_code == 200
    assert b'Вход в админ-панель' in response.data