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


class InstanceViewSet(ModelViewSet):
    renderer_classes = (ModelJSONRenderer, )

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        serializer_class = self.serializer_class
        if serializer_class is not None:
            return serializer_class

        assert self.model is not None, \
            "'%s' should either include a 'serializer_class' attribute, " \
            "or use the 'model' attribute as a shortcut for " \
            "automatically generating a serializer class." \
            % self.__class__.__name__

        class DefaultSerializer(self.model_serializer_class):
            class Meta:
                model = self.model
        return DefaultSerializer


    @classmethod
    def instance_rest_methods(cls):
        methods_items = inspect.getmembers(cls.model, predicate=inspect.ismethod)

        for method_name, method in methods_items:
            if hasattr(method, 'bind_to_methods'):
                yield method_name

    @classmethod
    def get_instance_method(cls, method_name):
        return getattr(cls.model, method_name)

    def __init__(self, **kwargs):
        super(InstanceViewSet, self).__init__(**kwargs)

        for method_name in self.instance_rest_methods():
            setattr(self, method_name, InstanceMethodWrapper(self, method_name))


__all__ = ['InstanceViewSet']