import inspect

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import ManyToManyField
from django.utils.functional import SimpleLazyObject
from enumfields.fields import EnumFieldMixin
from rest_framework.compat import get_concrete_model
from rest_framework.exceptions import ParseError
from rest_framework.serializers import ModelSerializer, _resolve_model
from rest_framework.fields import Field
from rest_framework import fields as rest_fields

from easyapi import BottomlessDict
from easyapi.fields import MetaField, RestEnumField


__author__ = 'mikhailturilin'


def model_serializer_class(model_class):
    class _DefaultSerializer(AutoModelSerializer):
        class Meta:
            model = model_class

    return _DefaultSerializer


def model_serializer(model_class, inner_dict=None, many=False):
     return model_serializer_class(model_class)(embedded_def_dict=inner_dict, many=many)


def serialize_model(model_class, instance, inner_dict, many=False):
    if not instance:
        return None
    new_serializer = model_serializer(model_class, inner_dict, many)
    return new_serializer.to_native(instance)


def serialize_instance(instance, embedded_dict=None, many=False):
    if isinstance(instance, SimpleLazyObject):
        instance = instance._wrapped

    return serialize_model(type(instance), instance, embedded_dict, many)


def serialize_queryset(related_model, qs, inner_dict):
    new_serializer = model_serializer(related_model, inner_dict)
    return [new_serializer.to_native(inst) for inst in qs]


def convert_result(value, embedded_def_dict, data_type, many):
    if many:
        return convert_many(sequence=value, embedded_def_dict=embedded_def_dict, data_type=data_type)
    else:
        return convert_one(obj=value, embedded_def_dict=embedded_def_dict, data_type=data_type)


def convert_many(sequence, embedded_def_dict, data_type):
    return [convert_one(obj, embedded_def_dict, data_type) for obj in sequence]


def convert_one(obj, embedded_def_dict, data_type):
    if data_type:
        if issubclass(data_type, Field):
            return data_type().to_native(obj)

        if callable(data_type):
            return data_type(obj)

    if not embedded_def_dict:
        return obj

    if isinstance(obj, models.Model):
        return serialize_model(type(obj), obj, embedded_def_dict)

def update_embedded_dict(embedded_dict, embedded_params):
    if embedded_params:
        for embedded_param in embedded_params:
            components = embedded_param.split('__')
            cur_dict = embedded_dict
            for c in components:
                cur_dict = cur_dict[c]


def parse_embedded_dict(embedded_params):
    embedded_def_dict = BottomlessDict()
    update_embedded_dict(embedded_def_dict, embedded_params)
    return embedded_def_dict


def embedded_dict_from_request(request):
    embedded_param = request.QUERY_PARAMS.get('_embedded', '')
    if embedded_param:
        initial = embedded_param.split(',')
    else:
        initial = None
    return parse_embedded_dict(initial)


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
        self.possible_embedded_names = set(
            self.related_fields_names +
            self.reverse_rel_names +
            self.embedded_function_names() +
            self.embedded_property_names())


    def get_embedded_def_dict(self):



        if self.embedded_def_dict:
            return self.embedded_def_dict

        try:
            embedded_def_dict = embedded_dict_from_request(self.context['request'])
        except (AttributeError, KeyError):
            # meaning no context is provided
            embedded_def_dict = BottomlessDict()


        update_embedded_dict(embedded_def_dict, getattr(self.model, 'rest_embedded', []))


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
                result[field_name] = serialize_model(related_model,
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
                result[relation_name] = serialize_queryset(related_model,
                                                           getattr(obj, relation_name).all(),
                                                           embedded_def_dict[relation_name])
            else:
                try:
                    instance = getattr(obj, relation_name)
                except ObjectDoesNotExist:
                    instance = None

                result[relation_name] = serialize_model(related_model,
                                                        instance,
                                                        embedded_def_dict[relation_name])

        # embedded functions
        for method_name, method in self.embedded_functions():
            if method_name and method_name in embedded_def_dict:
                embedded_result = method(obj)  # calling the method
                result[method_name] = convert_result(embedded_result,
                                                     embedded_def_dict[method_name],
                                                     getattr(method, 'rest_data_type', None),
                                                     getattr(method, 'rest_many', False))

        # embedded properties
        for prop_name, descriptor in self.embedded_properties():
            if prop_name and prop_name in embedded_def_dict:
                embedded_result = getattr(obj, prop_name)  # getting property value
                result[prop_name] = convert_result(embedded_result,
                                                   embedded_def_dict[prop_name],
                                                   getattr(descriptor, 'rest_data_type', None),
                                                   getattr(descriptor, 'rest_many', False))

        return result


    def embedded_function_names(self):
        return [method_name for method_name, method in self.embedded_functions()]


    def embedded_functions(self):
        return [(method.rest_embeddable_function, method) for method_name, method in
                class_functions_with_attr(self.model, 'rest_embeddable_function')]

    def embedded_property_names(self):
        return [prop_name for prop_name, descriptor in self.embedded_properties()]

    def embedded_properties(self):
        return [(getattr(descriptor, 'rest_embeddable_property') or descriptor.fget.__name__, descriptor) for
                prop_name, descriptor in class_properties_with_attr(self.model, 'rest_embeddable_property')]


def class_properties_with_attr(cls, flag_attribute):
    return inspect.getmembers(cls, predicate=lambda x: inspect.isdatadescriptor(x) and hasattr(x, flag_attribute))


def class_functions_with_attr(cls, flag_attribute):
    return inspect.getmembers(cls, predicate=lambda x: inspect.ismethod(x) and hasattr(x, flag_attribute))


class JsonField(rest_fields.Field):
    pass




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



        # adding fields for properties
        for p_name, p_val in class_properties_with_attr(cls, 'field_class'):
            field_name = getattr(p_val, 'name', p_name) or p_name  # we use property name as field name by default
            ret[field_name] = p_val.field_class(source=p_name)

        return ret


    def get_related_field_with_source(self, model_field, related_model, to_many, source):
        field = self.get_related_field(model_field, related_model, to_many)
        field.source = source
        return field

    def get_field(self, model_field):
        if isinstance(model_field, EnumFieldMixin):
            return RestEnumField(model_field.enum)

        return super(AutoModelSerializer, self).get_field(model_field)

