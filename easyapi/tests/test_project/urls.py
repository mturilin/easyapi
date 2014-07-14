from django.conf.urls import patterns, include, url

from django.contrib import admin
from easyapi.tests.test_project.api import router

admin.autodiscover()





urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'test_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
)
