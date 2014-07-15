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