from django.conf.urls import url, patterns, include
from django.contrib import admin
admin.autodiscover()
from .routers import router

urlpatterns = patterns('',
    # The qiprofile REST URLs.
    url(r'', include(router.urls, namespace='api')),
    # The test URLs.
    url(r'^test/', include('django_jasmine.urls', namespace='test')),
    # Django REST authorization.
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    # Uncomment the admin/doc line below to enable admin documentation.
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the admin line below to enable the admin page.
    # url(r'^admin/', include(admin.site.urls)),
)
