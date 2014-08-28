from enum import Enum
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.encoders import JSONEncoder
from django.db import models
from django.utils.functional import SimpleLazyObject

from easyapi.fields import enum_value
from easyapi.serializer import AutoModelSerializer


__author__ = 'mikhailturilin'


class ModelJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, models.Model):
            if isinstance(o, SimpleLazyObject):
                o = o._wrapped

            class DefaultSerializer(AutoModelSerializer):
                class Meta:
                    model = type(o)

            serializer = DefaultSerializer(instance=o)
            return serializer.data

        elif isinstance(o, Enum):
            return enum_value(o)

        else:
            return super(ModelJSONEncoder, self).default(o)


class ModelJSONRenderer(JSONRenderer):
    encoder_class = ModelJSONEncoder