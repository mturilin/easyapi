from functools import wraps
from django.http.response import HttpResponseBadRequest

from rest_framework.fields import Field

from .params import extract_rest_params


__author__ = 'mikhailturilin'


def rest_method(rest_verbs=None, arg_types=None, data_type=None, many=False):
    """
    Decorator that saves the function's rest args and verbs definitions to be used later in the InstanceViewSet
    :param rest_verbs:
    :param arg_types:
    :return:
    """
    rest_verbs = rest_verbs or ['GET']
    arg_types = arg_types or {}

    def outer(function):
        function.bind_to_methods = rest_verbs
        function.arg_types = arg_types
        function.data_type = data_type
        function.many = many
        return function

    return outer


def map_params(**param_dict):
    def outer(func):
        @wraps(func)
        def inner_func(request, *args, **kwargs):
            new_kwargs = extract_rest_params(request, param_dict)

            kwargs.update(new_kwargs)
            return func(request, *args, **kwargs)

        @wraps(func)
        def inner_method(self, request, *args, **kwargs):
            new_kwargs = extract_rest_params(request, param_dict)

            kwargs.update(new_kwargs)

            try:
                result = func(self, request, *args, **kwargs)
            except StandardError as err:
                if isinstance(err, (ValueError, LookupError)):
                    return HttpResponseBadRequest(err)
                raise err

            return result

        if 'self' in func.func_code.co_varnames:
            return inner_method
        else:
            return inner_func

    return outer


def rest_property(property_data_type=Field, property_name=None):
    class RestProperty(Property):
        field_class = property_data_type
        name = property_name

    return RestProperty


def rest_embeddable_property(name=None, many=False, data_type=None):
    class RestProperty(Property):
        rest_embeddable_property = name
        rest_many = many
        rest_data_type = data_type

    return RestProperty


def rest_embeddable_function(name=None, many=False, data_type=None):
    def outer(func):
        func.rest_embeddable_function = name or func.__name__
        func.rest_many = many
        func.rest_data_type = data_type

        return func

    return outer


class Property(object):
    "Emulate PyProperty_Type() in Objects/descrobject.c"

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)