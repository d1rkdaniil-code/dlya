def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Python' in response.data

def test_contact_get(client):
    response = client.get('/contact')
    assert response.status_code == 200
    assert b'captcha' in response.data