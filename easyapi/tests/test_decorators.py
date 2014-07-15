import json

__author__ = 'mikhailturilin'


def test_func_decorator(api_client):
    response = api_client.get('/custom-api/hello-func/', {'name':'Misha'})
    response_data = json.loads(response.content)

    assert 'Hello, Misha' in response_data


def test_method_decorator(api_client):
    response = api_client.get('/custom-api/hello-view/', {'name':'Misha'})
    response_data = json.loads(response.content)

    assert 'Hello, Misha' in response_data



