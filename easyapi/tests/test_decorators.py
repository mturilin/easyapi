import json
import pytest
from rest_framework.status import HTTP_400_BAD_REQUEST
from easyapi.decorators import unfilled_required_params

__author__ = 'mikhailturilin'


@pytest.mark.django_db
def test_func_decorator(staff_api_client):
    response = staff_api_client.get('/custom-api/hello-func/', {'name':'Misha'})
    response_data = json.loads(response.content)

    assert 'Hello, Misha' in response_data

@pytest.mark.django_db
def test_func_decorator_no_val(staff_api_client):
    response = staff_api_client.get('/custom-api/hello-func/')
    assert response.status_code == HTTP_400_BAD_REQUEST

    assert response.content == "Required params (name) are not specified"


@pytest.mark.django_db
def test_method_decorator(staff_api_client):
    response = staff_api_client.get('/custom-api/hello-view/', {'name':'Misha'})
    assert response.status_code == 200
    response_data = json.loads(response.content)

    assert 'Hello, Misha' in response_data



@pytest.mark.django_db
def test_method_decorator_no_val(staff_api_client):
    response = staff_api_client.get('/custom-api/hello-view/')
    assert response.status_code == HTTP_400_BAD_REQUEST

    assert response.content == "Required params (name) are not specified"




def test_unfilled_non_default_params():
    def a(param1, param2, param3=1, param4=2):
        pass

    def b(param1, param2):
        pass

    assert unfilled_required_params(a, ['param1 value'], {'param4':1}) == {'param2'}
    assert unfilled_required_params(a, [], {}) == {'param1','param2'}
    assert unfilled_required_params(a, ['param1','param2'], {'param4':1}) == set()
    assert unfilled_required_params(b, ['param1'], {}) == {'param2'}

