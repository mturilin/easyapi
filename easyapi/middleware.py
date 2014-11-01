from django.http import HttpResponse
from rest_framework.status import HTTP_400_BAD_REQUEST

from easyapi.errors import BadRequestError


__author__ = 'michaelturilin'


class BadRequestMiddleware(object):
    """
    This class returns HTTP Bad Request (400)
    status for the requests that raise ValueError and descendants.
    """

    def process_exception(self, request, exception):
        if isinstance(exception, (ValueError, BadRequestError)):
            return HttpResponse(exception, status=HTTP_400_BAD_REQUEST)