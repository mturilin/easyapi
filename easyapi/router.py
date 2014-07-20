from django.db.models import get_models, get_app
from rest_framework.routers import DefaultRouter, flatten, Route, replace_methodname
from django.core.exceptions import ImproperlyConfigured
from rest_framework import views
from rest_framework.response import Response
from rest_framework.reverse import reverse

from easyapi.permissions import IsStaff
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

MANAGER_METHOD_ROUTE = Route(
    url=r'^{prefix}-manager/{methodname}{trailing_slash}$',
    mapping={
        '{httpmethod}': '{methodname}',
    },
    name='{basename}-manager-{methodnamehyphen}',
    initkwargs={}
)


class EasyApiRouter(DefaultRouter):
    permission_classes = (IsStaff,)


    def __init__(self, namespace=None, **kwargs):
        super(EasyApiRouter, self).__init__(**kwargs)
        self.namespace = namespace


    def known_actions(self):
        the_known_actions = flatten([route.mapping.values() for route in self.routes])
        return the_known_actions

    def compute_routes(self, wrapper, method_name, route):
        httpmethods = wrapper.bind_to_methods

        dynamic_routes = []
        if httpmethods:
            if method_name in self.known_actions():
                raise ImproperlyConfigured('Cannot use @rest_method decorator on '
                                           'method "%s" as it is an existing route' % method_name)
            httpmethods = [method.lower() for method in httpmethods]
            dynamic_routes.append((httpmethods, method_name))


        # Dynamic routes (@link or @action decorator)
        instance_routes = []
        for httpmethods, method_name in dynamic_routes:
            initkwargs = route.initkwargs.copy()
            # initkwargs.update(getattr(viewset, method_name).kwargs)
            instance_routes.append(Route(
                url=replace_methodname(route.url, method_name),
                mapping=dict((httpmethod, method_name) for httpmethod in httpmethods),
                name=replace_methodname(route.name, method_name),
                initkwargs=initkwargs,
            ))

        return instance_routes

    def get_routes(self, viewset):
        routes = super(EasyApiRouter, self).get_routes(viewset)

        if issubclass(viewset, InstanceViewSet):
            for method_name in viewset.instance_rest_methods():
                inst_wrapper = viewset.get_instance_method(method_name)
                instance_routes = self.compute_routes(inst_wrapper, method_name, INSTANCE_METHOD_ROUTE)

                routes.extend(instance_routes)

            for method_name in viewset.manager_rest_methods():
                inst_wrapper = viewset.get_manager_method(method_name)
                manager_routes = self.compute_routes(inst_wrapper, method_name, MANAGER_METHOD_ROUTE)

                routes.extend(manager_routes)

        return routes

    def get_method_map(self, viewset, method_map):
        is_instance_viewset = issubclass(viewset, InstanceViewSet)

        bound_methods = {}
        for method, action in method_map.items():
            if hasattr(viewset, action) \
                    or (is_instance_viewset and action in viewset.instance_rest_methods()) \
                    or (is_instance_viewset and action in viewset.manager_rest_methods()):
                bound_methods[method] = action
        return bound_methods


    def get_api_root_view(self):
        """
        I ovveriden this function to include namespaces
        """
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)

        outer_self = self

        class APIRoot(views.APIView):
            _ignore_model_permissions = True
            permission_classes = outer_self.permission_classes

            def get(self, request, format=None):
                ret = {}
                for key, url_name in api_root_dict.items():
                    if outer_self.namespace:
                        url_name = "%s:%s" % (outer_self.namespace, url_name)
                    ret[key] = reverse(url_name, request=request, format=format)
                return Response(ret)

        return APIRoot.as_view()

    @property
    def urls(self):
        urls = super(EasyApiRouter, self).urls
        if self.namespace:
            return urls, self.namespace, self.namespace

        return urls


def ViewSetFactory(the_model):
    class _ModelViewSet(InstanceViewSet):
        model = the_model

    return _ModelViewSet


class AutoAppRouter(EasyApiRouter):
    def __init__(self, app_name, **kwargs):
        super(AutoAppRouter, self).__init__(**kwargs)

        app = get_app(app_name)
        for model in get_models(app):
            viewset_class = ViewSetFactory(model)
            self.register(model.__name__.lower(), viewset_class)


class AutoAppListRouter(EasyApiRouter):
    def __init__(self, *app_names, **kwargs):
        super(AutoAppListRouter, self).__init__(**kwargs)

        for app_name in app_names:
            app = get_app(app_name)
            for model in get_models(app):
                viewset_class = ViewSetFactory(model)
                prefix = "%s/%s" % (app_name, model.__name__.lower())
                self.register(prefix, viewset_class)


