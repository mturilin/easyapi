from functools import wraps
from django.http.response import HttpResponseBadRequest

from rest_framework.fields import Field
from easyapi.errors import BadRequestError

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

def check_unfilled_required_params(func, args, kwargs):
    unfilled = unfilled_required_params(func, args, kwargs)
    if unfilled:
        param_list_str = ", ".join(unfilled)
        raise BadRequestError("Required params (%s) are not specified" % param_list_str)


def unfilled_required_params(func, args, kwargs):
    """
    Returns the list of unfilled non-default params, which:
        - Don't have default values
        - Are not filled using args
        - Are not filled using kwargs
    """
    arguments = func.func_code.co_varnames[:func.func_code.co_argcount] # slicing to cut off * and ** args
    defaults = func.func_defaults

    num_of_defaults = len(defaults or [])

    # non default params are all params except the last "num_of_defaults"  could be empty
    non_default_args = arguments[:-num_of_defaults] if num_of_defaults else arguments

    # some the params are filled positionally with args
    unfilled_positionally_non_default_args = non_default_args[len(args):]

    # so the real unfilled params are those which are also not filled using kwargs
    unfilled_non_default_args = set(unfilled_positionally_non_default_args) - set(kwargs.keys())

    return unfilled_non_default_args



def map_params(**param_dict):
    def outer(func):
        @wraps(func)
        def inner_func(request, *args, **kwargs):
            new_kwargs = extract_rest_params(request, param_dict)
            kwargs.update(new_kwargs)

            check_unfilled_required_params(func, [request] + list(args), kwargs)

            return func(request, *args, **kwargs)

        @wraps(func)
        def inner_method(self, request, *args, **kwargs):
            new_kwargs = extract_rest_params(request, param_dict)

            kwargs.update(new_kwargs)

            check_unfilled_required_params(func, [self, request] + list(args), kwargs)

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