from functools import wraps

from .params import extract_rest_params


__author__ = 'mikhailturilin'


def rest_method(rest_verbs=None, arg_types=None):
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
            return func(self, request, *args, **kwargs)

        if 'self' in func.func_code.co_varnames:
            return inner_method
        else:
            return inner_func

    return outer



def rest_property(property_data_type, property_name=None):
    class RestProperty(Property):
        field_class = property_data_type
        name = property_name

    return RestProperty


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