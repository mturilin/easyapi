from enum import Enum
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.encoders import JSONEncoder
from django.db import models

from easyapi.fields import enum_value
from easyapi.serializer import serialize_instance


__author__ = 'mikhailturilin'


class ModelJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, models.Model):
            return serialize_instance(o)

        elif isinstance(o, Enum):
            return enum_value(o)

        elif hasattr(o, 'to_json'):
            return o.to_json()

        else:
            return super(ModelJSONEncoder, self).default(o)


class ModelJSONRenderer(JSONRenderer):
    encoder_class = ModelJSONEncoder