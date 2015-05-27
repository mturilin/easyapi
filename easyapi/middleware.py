from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponse
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from easyapi.errors import BadRequestError


__author__ = 'michaelturilin'


class HttpErrorsMiddleware(object):
    """
    This class returns the following HTTP message codes:
    - Bad Request (400) for ValueError and descendants.
    - Not Found (404) for Django's ObjectDoesNotExists
    """

    def process_exception(self, request, exception):
        if isinstance(exception, (ValueError, BadRequestError)):
            return HttpResponse(exception, status=HTTP_400_BAD_REQUEST)

        if isinstance(exception, (ObjectDoesNotExist,)):
            return HttpResponse(exception, status=HTTP_404_NOT_FOUND)

        if isinstance(exception, (MultipleObjectsReturned,)):
            return HttpResponse(exception, status=HTTP_409_CONFLICT)

