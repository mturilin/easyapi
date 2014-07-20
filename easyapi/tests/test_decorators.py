import json
import pytest

__author__ = 'mikhailturilin'


@pytest.mark.django_db
def test_func_decorator(staff_api_client):
    response = staff_api_client.get('/custom-api/hello-func/', {'name':'Misha'})
    response_data = json.loads(response.content)

    assert 'Hello, Misha' in response_data


@pytest.mark.django_db
def test_method_decorator(staff_api_client):
    response = staff_api_client.get('/custom-api/hello-view/', {'name':'Misha'})
    response_data = json.loads(response.content)

    assert 'Hello, Misha' in response_data



