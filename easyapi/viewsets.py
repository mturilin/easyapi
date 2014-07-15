import inspect

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from easyapi.encoder import ModelJSONRenderer
from easyapi.params import extract_rest_params


__author__ = 'mikhailturilin'


class InstanceMethodWrapper(object):
    def __init__(self, viewset, method_name):
        self.viewset = viewset
        self.method_name = method_name
        self.method = getattr(viewset.model, self.method_name)
        self.bind_to_methods = self.method.bind_to_methods
        self.arg_types = getattr(self.method, 'arg_types', {})

    def __call__(self, request, *args, **kwargs):
        instance = self.viewset.get_object()
        params = extract_rest_params(request, self.arg_types)
        result = self.method(instance, **params)
        return Response(result)


class ManagerMethodWrapper(object):
    def __init__(self, manager, method_name):
        self.method_name = method_name
        self.manager = manager
        self.method = getattr(self.manager, self.method_name)
        self.bind_to_methods = self.method.bind_to_methods
        self.arg_types = getattr(self.method, 'arg_types', {})

    def __call__(self, request, *args, **kwargs):
        params = extract_rest_params(request, self.arg_types)
        result = self.method(**params)
        return Response(result)


class InstanceViewSet(ModelViewSet):
    renderer_classes = (ModelJSONRenderer, )


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