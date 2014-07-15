from django.conf.urls import patterns, include, url

from django.contrib import admin
from easyapi.tests.test_project.api import router, auto_router
from easyapi.tests.test_project.views import WelcomeView

admin.autodiscover()





urlpatterns = patterns('easyapi.tests.test_project.views',
    # Examples:
    # url(r'^$', 'test_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^auto-api/', include(auto_router.urls)),
    url(r'^custom-api/hello-func/', 'say_hello'),
    url(r'^custom-api/hello-view/', WelcomeView.as_view()),
)
