from django.conf.urls import patterns, url
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

__author__ = 'mikhailturilin'


def enum_view_name(enum):
    return "list-%s" % enum.__name__


def enum_list_view(enum):
    @api_view(['GET'])
    def view(request):
        return Response([enum_to_dict(enum_val) for enum_val in enum])

    return view


def enum_to_dict(enum_val):
    return {
        'name': enum_val.name,
        'value': enum_val.value,
        'full_name': str(enum_val),
        'type': type(enum_val).__name__
    }


def enum_url(enum):
    return url(r'^%s/$' % enum.__name__.lower(), enum_list_view(enum), name=enum_view_name(enum))


class EnumRouter(object):
    def __init__(self, enum_list, namespace=None):
        self.enum_list = enum_list
        self.namespace = namespace


    @property
    def urls(self):
        urls = patterns('', *self.build_urls())
        if self.namespace:
            return urls, self.namespace, self.namespace

        return urls


    def build_urls(self):
        return [enum_url(enum) for enum in self.enum_list] + [self.get_root_view_url()]

    def get_root_view_url(self):
        return url('^$', self.get_root_view())

    def get_root_view(self):
        @api_view(['GET'])
        def view(request):
            return Response({
                enum.__name__: reverse(self.enum_view_name_namespace(enum)) for enum in self.enum_list
            })

        return view

    def enum_view_name_namespace(self, enum):
        if self.namespace:
            prefix = '%s:' % self.namespace
        else:
            prefix = ''

        return prefix + enum_view_name(enum)
