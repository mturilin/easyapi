from django.contrib.auth import get_user_model
import pytest
from rest_framework.request import Request
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.views import APIView

__author__ = 'mikhailturilin'




class RestAPIRequestFactory(APIRequestFactory):
    def request(self, **kwargs):
        request = super(APIRequestFactory, self).request(**kwargs)
        request._dont_enforce_csrf_checks = not self.enforce_csrf_checks
        return Request(request, parsers=APIView().get_parsers())


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
@pytest.mark.django_db
def user_api_client():
    credentials = dict(username="aaa", password='bbb')
    user = get_user_model().objects.create_user(**credentials)
    client = APIClient()
    client.login(**credentials)
    return client


@pytest.fixture
@pytest.mark.django_db
def staff_api_client():
    credentials = dict(username="ccc", password='ddd')
    user = get_user_model().objects._create_user(is_staff=True, email=None, is_superuser=False, **credentials)
    client = APIClient()
    client.login(**credentials)
    return client



@pytest.fixture
@pytest.mark.django_db
def admin_api_client():
    credentials = dict(username="eee", password='fff')
    user = get_user_model().objects.create_superuser(**credentials)
    client = APIClient()
    client.login(**credentials)
    return client


@pytest.fixture
def api_request_factory():
    return RestAPIRequestFactory()