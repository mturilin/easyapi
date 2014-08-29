import inspect

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from easyapi.encoder import ModelJSONRenderer
from easyapi.filters import QuerySetFilterBackend, FILTER_ALL
from easyapi.params import extract_rest_params
from easyapi.permissions import IsStaff
from easyapi.serializer import AutoModelSerializer, convert_result, embedded_dict_from_request


__author__ = 'mikhailturilin'


class InstanceMethodWrapper(object):
    def __init__(self, viewset, method_name):
        self.viewset = viewset
        self.method_name = method_name
        self.method = getattr(viewset.model, self.method_name)
        self.bind_to_methods = self.method.bind_to_methods
        self.arg_types = getattr(self.method, 'arg_types', {})
        self.data_type = getattr(self.method, 'data_type', None)
        self.many = getattr(self.method, 'many', False)

    def __call__(self, request, *args, **kwargs):
        instance = self.viewset.get_object()
        params = extract_rest_params(request, self.arg_types)
        result = self.method(instance, **params)
        converted_result = convert_result(result, embedded_dict_from_request(request), self.data_type, self.many)
        return Response(converted_result)


class ManagerMethodWrapper(object):
    def __init__(self, manager, method_name):
        self.method_name = method_name
        self.manager = manager
        self.method = getattr(self.manager, self.method_name)
        self.bind_to_methods = self.method.bind_to_methods
        self.arg_types = getattr(self.method, 'arg_types', {})
        self.data_type = getattr(self.method, 'data_type', None)
        self.many = getattr(self.method, 'many', False)

    def __call__(self, request, *args, **kwargs):
        params = extract_rest_params(request, self.arg_types)
        result = self.method(**params)
        converted_result = convert_result(result, embedded_dict_from_request(request), self.data_type, self.many)
        return Response(converted_result)


class InstanceViewSet(ModelViewSet):
    model_serializer_class = AutoModelSerializer

    permission_classes = (IsStaff,)

    renderer_classes = (ModelJSONRenderer, )
    filter_backend = QuerySetFilterBackend

    filtering = {
        '*': {
            'filters': FILTER_ALL
        }
    }


    @classmethod
    def instance_rest_methods(cls):
        methods_items = inspect.getmembers(cls.model, predicate=inspect.ismethod)

        for method_name, method in methods_items:
            if hasattr(method, 'bind_to_methods'):
                yield method_name

    @classmethod
    def manager_rest_methods(cls):
        methods_items = inspect.getmembers(cls.model.objects, predicate=inspect.ismethod)

        for method_name, method in methods_items:
            if hasattr(method, 'bind_to_methods'):
                yield method_name

    @classmethod
    def get_instance_method(cls, method_name):
        return getattr(cls.model, method_name)

    @classmethod
    def get_manager_method(cls, method_name):
        return getattr(cls.model.objects, method_name)

    def __init__(self, **kwargs):
        super(InstanceViewSet, self).__init__(**kwargs)

        for method_name in self.instance_rest_methods():
            setattr(self, method_name, InstanceMethodWrapper(self, method_name))

        for method_name in self.manager_rest_methods():
            setattr(self, method_name, ManagerMethodWrapper(self.model.objects, method_name))


__all__ = ['InstanceViewSet']