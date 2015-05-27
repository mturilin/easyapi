import json
import types
import warnings

from django.db.models import Model
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MergeDict
import isodate
from rest_framework.exceptions import ParseError


__author__ = 'mturilin'


def convert_param_value(param_type, param_value):
    if isinstance(param_type, Model):
        return param_type.objects.get(id=int(param_value))

    return param_type(param_value)


def required_params(func, skip_self=False):
    """
    Returns the list of unfilled non-default params, which:
        - Don't have default values
        - Are not filled using args
        - Are not filled using kwargs
    """
    arguments = func.func_code.co_varnames[:func.func_code.co_argcount]  # slicing to cut off * and ** args
    defaults = func.func_defaults

    num_of_defaults = len(defaults or [])

    # non default params are all params except the last "num_of_defaults"  could be empty
    non_default_args = arguments[:-num_of_defaults] if num_of_defaults else arguments

    if skip_self:
        if len(non_default_args) == 0 or non_default_args[0] != 'self':
            warnings.warn("Skipping self for required params failed")
        return non_default_args[1:]

    return non_default_args


def extract_rest_params(request, param_types, required_params=None):
    required_params = required_params or []

    new_kwargs = {}

    request_dicts = [getattr(request, name, {}) for name in {'DATA', 'GET', 'POST'}]
    data_dict = MergeDict(*request_dicts)

    for (param_name, param_type) in param_types.iteritems():

        if param_name not in data_dict:
            if param_name in required_params:
                raise ParseError('Param "%s" is required' % param_name)
            continue

        param_value = data_dict[param_name]

        new_kwargs[param_name] = convert_param_value(param_type, param_value)

    return new_kwargs


# Converters

def smart_bool(value):
    return value.lower() in ("yes", "true", "t", "1")


iso_datetime = isodate.parse_datetime
iso_date = isodate.parse_date


def model_param(model):
    def inner(pk):
        return model.objects.get(pk=pk)

    return inner


json_param = json.loads


def list_param(list_str):
    if isinstance(list_str, types.ListType):
        return list_str

    if not isinstance(list_str, types.StringTypes):
        raise ValueError('Value of is not of the list type %s' % list_str)

    if list_str.startswith('[') and list_str.endswith(']'):
        return json.loads(list_str)

    return list_str.split(',')


def primary_key(model):
    def inner(id):
        return get_object_or_404(model, id=id)

    return inner




