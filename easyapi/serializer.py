from django.db.models import Model
from django.db import models
from rest_framework.compat import get_concrete_model
from rest_framework.exceptions import ParseError
from rest_framework.fields import Field
from rest_framework.serializers import ModelSerializer, _resolve_model

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

    def get_fields(self):
        the_fields = super(AutoModelSerializer, self).get_fields()
        model = self.opts.model

        try:
            the_fields.update(model.extra_rest_fields)
        except AttributeError:
            pass

        return the_fields

    def get_default_fields(self):
        ret = super(AutoModelSerializer, self).get_default_fields()

        # Deal with forward relationships
        cls = self.opts.model
        opts = get_concrete_model(cls)._meta
        nested = bool(self.opts.depth)

        forward_rels = [field for field in opts.fields if field.serialize]
        forward_rels += [field for field in opts.many_to_many if field.serialize]

        for model_field in forward_rels:
            has_through_model = False
            field_name = model_field.name

            if model_field.rel:
                to_many = isinstance(model_field, models.fields.related.ManyToManyField)
                related_model = _resolve_model(model_field.rel.to)

                if to_many and not model_field.rel.through._meta.auto_created:
                    has_through_model = True

            if model_field.rel and nested:
                field = self.get_nested_field(model_field, related_model, to_many)
            elif model_field.rel:
                field = self.get_related_field(model_field, related_model, to_many)
                field_name += '_id'
            else:
                field = self.get_field(model_field)

            if field:
                if has_through_model:
                    field.read_only = True

                ret[field_name] = field

        return ret
