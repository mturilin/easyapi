import inspect

from django.core.exceptions import ImproperlyConfigured
from django.http.response import Http404
from rest_framework.response import Response

from rest_framework.routers import DefaultRouter, flatten, Route, replace_methodname
from easyapi.viewsets import InstanceViewSet


__author__ = 'mikhailturilin'

INSTANCE_METHOD_ROUTE = Route(
    url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
    mapping={
        '{httpmethod}': '{methodname}',
    },
    name='{basename}-{methodnamehyphen}',
    initkwargs={}
)





class EasyApiRouter(DefaultRouter):
    def __init__(self):
        super(EasyApiRouter, self).__init__()


    def known_actions(self):
        the_known_actions = flatten([route.mapping.values() for route in self.routes])
        return the_known_actions

    def get_routes(self, viewset):
        routes = super(EasyApiRouter, self).get_routes(viewset)


        if issubclass(viewset, InstanceViewSet):
            methods = viewset.instance_rest_methods()

            # Determine any `@action` or `@link` decorated methods on the viewset
            dynamic_routes = []
            for method_name in methods:
                inst_wrapper = viewset.get_instance_method(method_name)
                httpmethods = inst_wrapper.bind_to_methods

                if httpmethods:
                    if method_name in self.known_actions():
                        raise ImproperlyConfigured('Cannot use @rest_method decorator on '
                                                   'method "%s" as it is an existing route' % method_name)
                    httpmethods = [method.lower() for method in httpmethods]
                    dynamic_routes.append((httpmethods, method_name))

            for route in self.routes:
                if route.mapping == {'{httpmethod}': '{methodname}'}:
                    # Dynamic routes (@link or @action decorator)
                    for httpmethods, method_name in dynamic_routes:
                        initkwargs = route.initkwargs.copy()
                        #initkwargs.update(getattr(viewset, method_name).kwargs)
                        routes.append(Route(
                            url=replace_methodname(route.url, method_name),
                            mapping=dict((httpmethod, method_name) for httpmethod in httpmethods),
                            name=replace_methodname(route.name, method_name),
                            initkwargs=initkwargs,
                        ))

        return routes

    def get_method_map(self, viewset, method_map):
        is_instance_viewset = issubclass(viewset, InstanceViewSet)

        bound_methods = {}
        for method, action in method_map.items():
            if hasattr(viewset, action) or (is_instance_viewset and action in viewset.instance_rest_methods()):
                bound_methods[method] = action
        return bound_methods







