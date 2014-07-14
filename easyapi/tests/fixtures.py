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
def api_request_factory():
    return RestAPIRequestFactory()