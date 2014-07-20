import pytest
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_200_OK

__author__ = 'mikhailturilin'

@pytest.mark.django_db
@pytest.mark.parametrize('url',['/auto-api/company/','/auto-api/'])
def test_no_unlogged_access(api_client, url):
    response = api_client.get(url)

    assert response.status_code in [HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED]




@pytest.mark.django_db
def test_no_logged_regular_user_access(user_api_client):
    response = user_api_client.get('/auto-api/company/')

    assert response.status_code in [HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED]


@pytest.mark.django_db
def test_staff_access(staff_api_client):
    response = staff_api_client.get('/auto-api/')

    assert response.status_code == HTTP_200_OK



