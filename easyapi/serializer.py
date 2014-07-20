from django.db.models import Model
from django.db import models
from rest_framework.compat import get_concrete_model
from rest_framework.exceptions import ParseError
from rest_framework.fields import Field
from rest_framework.serializers import ModelSerializer, _resolve_model

from easyapi import BottomlessDict


__author__ = 'mikhailturilin'



class AutoModelSerializer(ModelSerializer):

    def __init__(self, instance=None, data=None, files=None, context=None, partial=False, many=None,
                 allow_add_remove=False, embedded_def_dict=None, **kwargs):
        self.embedded_def_dict = embedded_def_dict
        super(AutoModelSerializer, self).__init__(instance, data, files, context, partial, many, allow_add_remove,
                                                  **kwargs)

    def get_fields(self):
        the_fields = super(AutoModelSerializer, self).get_fields()
        model = self.opts.model

        try:
            the_fields.update(model.extra_rest_fields)
        except AttributeError:
            pass

        return the_fields

    def get_default_fields(self):
        """
        Overriding get_default_fields to do two things:
        1. Add nested models as serializer fields
        2. Add suffix '_id' to all foreign keys
        """
        ret = super(AutoModelSerializer, self).get_default_fields()

        embedded_def_dict = self.get_embedded_def_dict() or {}

        # Deal with forward relationships
        cls = self.opts.model
        opts = get_concrete_model(cls)._meta

        related_fields = [field for field in opts.fields if field.serialize if field.rel]

        # checking that there are no unknown embedded fields
        related_fields_names = set([field.name for field in related_fields])
        for key in embedded_def_dict.keys():
            if key not in related_fields_names:
                raise ParseError('Unknown embedded field %s' % key)


        for model_field in related_fields:
            field_name = model_field.name

            del ret[field_name]
            to_many = isinstance(model_field, models.fields.related.ManyToManyField)
            related_model = _resolve_model(model_field.rel.to)

            if field_name in embedded_def_dict:
                nested_field = self.nested_model_serializer(related_model, embedded_def_dict[field_name])
                nested_field.read_only = True
                ret[field_name] = nested_field

            ret[field_name + '_id'] = self.get_related_field(model_field, related_model, to_many)

        return ret


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

    def nested_model_serializer(self, related_model, inner_dict):
        class _DefaultSerializer(AutoModelSerializer):
            class Meta:
                model = related_model

        return _DefaultSerializer(embedded_def_dict=inner_dict)