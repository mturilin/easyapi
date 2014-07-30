from django.db.models import ManyToManyField

from rest_framework.compat import get_concrete_model
from rest_framework.exceptions import ParseError
from rest_framework.serializers import ModelSerializer, _resolve_model
from rest_framework.fields import Field

from easyapi import BottomlessDict
from easyapi.fields import MetaField


__author__ = 'mikhailturilin'


class EmbeddedObjectsField(Field):
    def __init__(self, model, embedded_def_dict=None):
        super(EmbeddedObjectsField, self).__init__()
        self.model = model
        self.embedded_def_dict = embedded_def_dict

        self.opts = get_concrete_model(self.model)._meta
        self.related_fields = [field for field in self.opts.fields if field.serialize if field.rel]
        self.reverse_rels = self.opts.get_all_related_objects() + self.opts.get_all_related_many_to_many_objects()

        self.related_fields_names = [field.name for field in self.related_fields]
        self.reverse_rel_names = [relation.get_accessor_name() for relation in self.reverse_rels]
        self.possible_embedded_names = set(self.related_fields_names + self.reverse_rel_names)


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

        # checking that there are no unknown embedded fields
        for key in embedded_def_dict.keys():
            if key not in self.possible_embedded_names:
                raise ParseError('Unknown embedded field %s' % key)

        return embedded_def_dict


    def field_to_native(self, obj, the_field_name):
        result = {}

        embedded_def_dict = self.get_embedded_def_dict() or {}


        # for the foreign keys
        for model_field in self.related_fields:
            field_name = model_field.name

            related_model = _resolve_model(model_field.rel.to)

            if field_name in embedded_def_dict:
                result[field_name] = self.serialize_model(related_model,
                                                          getattr(obj, field_name),
                                                          embedded_def_dict[field_name])

        # for the reverse relations
        for relation in self.reverse_rels:
            relation_name = relation.get_accessor_name()

            if relation_name not in embedded_def_dict:
                continue

            related_model = relation.model
            to_many = relation.field.rel.multiple

            if to_many:
                result[relation_name] = self.serialize_queryset(related_model,
                                                         getattr(obj, relation_name).all(),
                                                         embedded_def_dict[relation_name])
            else:
                result[relation_name] = self.serialize_model(related_model,
                                                          getattr(obj, relation_name),
                                                          embedded_def_dict[relation_name])


        return result

    def nested_model_serializer(self, related_model, inner_dict, to_many=False):
        class _DefaultSerializer(AutoModelSerializer):
            class Meta:
                model = related_model

        return _DefaultSerializer(embedded_def_dict=inner_dict, many=to_many)

    def serialize_model(self, related_model, instance, inner_dict, to_many=False):
        new_serializer = self.nested_model_serializer(related_model, inner_dict, to_many)
        return new_serializer.to_native(instance)

    def serialize_queryset(self, related_model, qs, inner_dict):
        new_serializer = self.nested_model_serializer(related_model, inner_dict)
        return [new_serializer.to_native(inst) for inst in qs]


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
        2. Add suffix '_id' to all foreign keys
        """
        ret = super(AutoModelSerializer, self).get_default_fields()

        # Deal with forward relationships
        cls = self.opts.model
        opts = get_concrete_model(cls)._meta

        related_fields = [field for field in opts.fields if field.serialize if field.rel]

        # adding embedded fields for the foreign keys
        for model_field in related_fields:
            field_name = model_field.name

            del ret[field_name]
            to_many = isinstance(model_field, ManyToManyField)

            if not to_many:
                related_model = _resolve_model(model_field.rel.to)

                ret[field_name + '_id'] = self.get_related_field_with_source(model_field, related_model, to_many,
                                                                             source=field_name)

        # adding links field
        ret['_meta'] = MetaField()
        ret['_embedded'] = EmbeddedObjectsField(cls, embedded_def_dict=self.embedded_def_dict)

        return ret


    def get_related_field_with_source(self, model_field, related_model, to_many, source):
        field = self.get_related_field(model_field, related_model, to_many)
        field.source = source
        return field