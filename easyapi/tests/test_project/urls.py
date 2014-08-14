from django.conf.urls import patterns, include, url
from django.contrib import admin
from easyapi.enums import EnumRouter

from easyapi.router import AutoAppListRouter, AutoAppRouter
from easyapi.tests.test_project.api import router
from easyapi.tests.test_project.models import CompanyType, ProjectScope
from easyapi.tests.test_project.views import WelcomeView


admin.autodiscover()

auto_list_router = AutoAppListRouter('test_project', namespace="list")
auto_router = AutoAppRouter('test_project', namespace='normal')
enum_router = EnumRouter([CompanyType, ProjectScope])

urlpatterns = patterns(
    'easyapi.tests.test_project.views',
    # Examples:
    # url(r'^$', 'test_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^enums/', include(enum_router.urls)),
    url(r'^auto-list/', include(auto_list_router.urls)),
    url(r'^auto-api/', include(auto_router.urls)),
    url(r'^custom-api/hello-func/', 'say_hello'),
    url(r'^custom-api/company-paginator/', 'company_paginator'),
    url(r'^custom-api/hello-view/', WelcomeView.as_view()),
)
