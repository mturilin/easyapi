from django.db.models import Model
from rest_framework.exceptions import ParseError
from rest_framework.fields import Field
from easyapi import serializer

__author__ = 'mikhailturilin'


class PrimaryKeyReadOnlyField(Field):
    def to_native(self, value):
        return value and value.pk





