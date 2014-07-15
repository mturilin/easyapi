from rest_framework.renderers import JSONRenderer
from rest_framework.utils.encoders import JSONEncoder
from django.db import models

from easyapi.serializer import AutoModelSerializer


__author__ = 'mikhailturilin'


class ModelJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, models.Model):
            class DefaultSerializer(AutoModelSerializer):
                class Meta:
                    model = type(o)

            serializer = DefaultSerializer(instance=o)
            return serializer.data
        else:
            return super(ModelJSONEncoder, self).default(o)


class ModelJSONRenderer(JSONRenderer):
    encoder_class = ModelJSONEncoder