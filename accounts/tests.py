import pytest
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_headless_allauth_login(client):
    username = 'testuser'
    password = 'testpassword123'
    email = 'testuser@example.com'
    User.objects.create_user(username=username, password=password, email=email)

    login_url = reverse('headless:browser:account:login')

    login_data = {
        'username': username,
        'password': password,
    }

    response = client.post(login_url, login_data, content_type='application/json')

    assert response.status_code == 200, response.content

    response_data = response.json()

    assert response_data['meta']['is_authenticated']
    assert response_data['data']['user']['email'] == email

    assert '_auth_user_id' in client.session
