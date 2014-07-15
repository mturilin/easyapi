from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from easyapi.decorators import map_params


__author__ = 'mikhailturilin'


@api_view(['GET'])
@map_params(name=str)
def say_hello(request, name):
    return Response("Hello, {name}".format(name=name))


class WelcomeView(APIView):
    @map_params(name=str)
    def get(self, request, name, **kwargs):
        return Response("Hello, {name}".format(name=name))