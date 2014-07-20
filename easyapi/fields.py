from django.db.models import Model
from rest_framework.exceptions import ParseError
from rest_framework.fields import Field

__author__ = 'mikhailturilin'


class PrimaryKeyReadOnlyField(Field):
    def to_native(self, value):
        return value and value.pk


class EmbeddedObjectsField(Field):
    def field_to_native(self, obj, field_name):
        """
        Given and object and a field name, returns the value that should be
        serialized for that field.
        """
        if obj is None:
            return self.empty
        try:
            request = self.context['request']
        except (AttributeError, KeyError):
            # meaning no context is provided
            return self.empty

        embedded_param = request.QUERY_PARAMS.get('_embedded', None)
        if not embedded_param:
            return self.empty

        embedded_fields = embedded_param.split(',')

        _embedded = {}

        for field_name in embedded_fields:
            try:
                value = getattr(obj, field_name)
                if isinstance(value, Model):
                    _embedded[field_name] = value
                else:
                    raise ParseError('Embedded field type must be Model, %s found' % str(type(value)))
            except AttributeError:
                raise ParseError('Unknown embedded field %s' % field_name)

        return _embedded




