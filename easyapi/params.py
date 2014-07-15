from decimal import Decimal
import json
import datetime
import types
import json as simplejson

from django.utils.datastructures import MergeDict
import dateutil.parser
import isodate
from rest_framework.exceptions import ParseError


__author__ = 'mturilin'


def multi_getattr(obj, attr, **kw):
    attributes = attr.split(".")
    for i in attributes:
        try:
            obj = getattr(obj, i)
            if not obj:
                return None
            if callable(obj):
                obj = obj()
        except AttributeError:
            if 'default' in kw:
                return kw['default']
            else:
                raise
    return obj


def subdict(dictionary, keys):
    return dict([(key, value) for (key, value) in dictionary.iteritems() if key in keys])


def obj_to_dict(obj, *args, **kwargs):
    """
    Creates a dict from the object's fields specified as keys. Supports attributes of several layer of
    depth.

    For example:
    class Car:
        wheel = Wheel()

        obj_to_dict(car, "name", wheeltype="wheel.type")

    would produce:
        {
            "name":...
            "wheeltype":...
        }

    """
    result_dict = {}
    for key in args:
        if "." in key:
            name = key.rsplit(".", 1)[1]
        else:
            name = key

        result_dict[name] = multi_getattr(obj, key)

    for name, key in kwargs.iteritems():
        if isinstance(key, types.FunctionType):
            result_dict[name] = key(obj)
        else:
            result_dict[name] = multi_getattr(obj, key)

    return result_dict


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



def extract_rest_params(request, param_types, required_params=None):
    required_params = required_params or []

    new_kwargs = {}

    data_dict = MergeDict(request.DATA, request.GET)

    for (param_name, param_type) in param_types.iteritems():

        if param_name not in data_dict:
            if param_name in required_params:
                raise ParseError('Param "%s" is required' % param_name)
            continue

        param_value = data_dict[param_name]

        new_kwargs[param_name] = param_type(param_value)

    return new_kwargs


def extract_rest_params_old(request, param_dict):
    """
    :param request: HttpRequest
    :param param_dict: param definitions
        int - integer
        str - string
        list - list of the values, each value of the list appear as separate param, like ?pages=1&pages=2&pages=3
        list[] - comma-separated list of values, like ?pages=1,2,3
        file - file uploaded in a form
        float - float
        bool - True, False, true, false
        date - date in iso8601
        json - url encoded json object
    :return: kwargs with extracted values
    """
    new_kwargs = {}
    if request.META.get('CONTENT_TYPE', "").startswith('application/json') and isinstance(request.DATA, dict):
        request_dict = MergeDict(request.REQUEST, request.DATA)
    else:
        request_dict = request.REQUEST
    for (param, p_type) in param_dict.iteritems():
        required = p_type.endswith('*')
        p_type = p_type.rstrip('*')

        if param not in request_dict:
            if required:
                raise ParseError('Param "%s" is required' % param)
            continue

        raw_value = request_dict.get(param, None)
        try:
            if p_type == 'json':
                p_value = json.loads(raw_value)

            elif p_type == 'list[]':
                if isinstance(raw_value, types.ListType):
                    p_value = raw_value
                elif isinstance(raw_value, types.StringTypes):
                    if raw_value.startswith('[') and raw_value.endswith(']'):
                        p_value = json.loads(raw_value)
                    else:
                        p_value = raw_value.split(',')
                else:
                    raise ValueError('Value of parameter % is not of the list type %s' % (param, raw_value))


            elif p_type == 'bool':
                if isinstance(raw_value, bool):
                    p_value = raw_value
                else:
                    p_value = smart_bool(raw_value)

            elif p_type == 'int':
                p_value = int(raw_value)

            elif p_type == 'float':
                p_value = float(raw_value)

            elif p_type == 'str':
                p_value = raw_value

            elif p_type.startswith('date'):
                if p_type.startswith('date:'):
                    date_format = p_type[5:]
                    p_value = datetime.datetime.strptime(raw_value, date_format)
                elif p_type == "date":
                    # use ISO 8601
                    p_value = dateutil.parser.parse(raw_value)
                else:
                    raise ValueError("Invalid date format '%s'" % p_type)
            elif p_type == "list":
                p_value = request_dict.getlist(param)
            else:
                raise ValueError('Unknown parameter type declaration %s' % p_type)
        except TypeError as err:
            raise ParseError("Error converting param %s=%s to type %s" % (param, repr(raw_value), p_type))

        new_kwargs[param] = p_value
    return new_kwargs


class JsonRestEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        else:
            return super(JsonRestEncoder, self).default(self, obj)


def this_domain_url(request, location):
    if not location.startswith("/"):
        location = "/" + location
    return '%s://%s%s' % (request.is_secure() and 'https' or 'http', request.get_host(), location)





