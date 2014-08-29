from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from easyapi.decorators import map_params
from easyapi.paginator import EasyPaginationSerializer
from easyapi.serializer import model_serializer_class
from easyapi.tests.test_project.models import Company


__author__ = 'mikhailturilin'


@api_view(['GET'])
@map_params(name=str)
def say_hello(request, name):
    return Response("Hello, {name}".format(name=name))


class WelcomeView(APIView):
    @map_params(name=str)
    def get(self, request, name, **kwargs):
        return Response("Hello, {name}".format(name=name))


class CompanyPaginator(EasyPaginationSerializer):
    class Meta:
        object_serializer_class = model_serializer_class(Company)


@api_view(['GET'])
def company_paginator(request):
    queryset = Company.objects.all()
    paginator = Paginator(queryset, 5)

    page_number = request.QUERY_PARAMS.get('page')
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999),
        # deliver last page of results.
        page = paginator.page(paginator.num_pages)

    serializer_context = {'request': request}
    serializer = CompanyPaginator(page, context=serializer_context)
    return Response(serializer.data)