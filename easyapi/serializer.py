from django.db.models import Model

from rest_framework.exceptions import ParseError
from rest_framework.fields import Field
from rest_framework.serializers import ModelSerializer

from easyapi import BottomlessDict


__author__ = 'mikhailturilin'


class EmbeddedObjectsField(Field):
    empty = {}

    def __init__(self, embedded_def_dict=None):
        super(EmbeddedObjectsField, self).__init__()
        self.embedded_def_dict = embedded_def_dict

    def get_embedded_def_dict(self):
        if self.embedded_def_dict:
            return self.embedded_def_dict

        try:
            request = self.context['request']
        except (AttributeError, KeyError):
            # meaning no context is provided
            return None

        embedded_param = request.QUERY_PARAMS.get('_embedded', None)

        if not embedded_param:
            return None

        embedded_def_dict = BottomlessDict()
        embedded_params = embedded_param.split(',')
        for embedded_param in embedded_params:
            components = embedded_param.split('__')
            cur_dict = embedded_def_dict
            for c in components:
                cur_dict = cur_dict[c]

        return embedded_def_dict

    def field_to_native(self, obj, embedded_param):
        """
        Given and object and a field name, returns the value that should be
        serialized for that field.
        """
        if obj is None:
            return self.empty


        embedded_def_dict = self.get_embedded_def_dict()

        if not embedded_def_dict:
            return self.empty

        _embedded = self.get_embedded(obj, embedded_def_dict)

        if not _embedded:
            return self.empty

        return _embedded

    def get_embedded(self, obj, embedded_def_dict):
        _embedded = {}

        for field_name, inner_dict in embedded_def_dict.iteritems():
            try:
                value = getattr(obj, field_name)
                if isinstance(value, Model):
                    _embedded[field_name] = self.serialize_model(value, inner_dict)
                else:
                    raise ParseError('Embedded field type must be Model, %s found' % str(type(value)))
            except AttributeError:
                raise ParseError('Unknown embedded field %s' % field_name)

        return _embedded


    def serialize_model(self, o, inner_dict):
        class _DefaultSerializer(AutoModelSerializer):
            _embedded = EmbeddedObjectsField(embedded_def_dict=inner_dict)
            class Meta:
                model = type(o)

        serializer = _DefaultSerializer(instance=o)
        return serializer.data


class AutoModelSerializer(ModelSerializer):
    _embedded = EmbeddedObjectsField()

    def get_fields(self):
        the_fields = super(AutoModelSerializer, self).get_fields()
        model = self.opts.model

        try:
            the_fields.update(model.extra_rest_fields)
        except AttributeError:
            pass

        return the_fields