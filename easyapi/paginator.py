from rest_framework import pagination
from rest_framework import serializers
from easyapi.serializer import AutoModelSerializer

__author__ = 'mikhailturilin'


class EasyPaginationSerializer(pagination.PaginationSerializer):
    num_pages = serializers.Field(source='paginator.num_pages')
    number = serializers.Field(source='number')
