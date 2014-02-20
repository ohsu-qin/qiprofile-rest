from django.conf.urls import url, patterns, include
from django.contrib import admin
admin.autodiscover()
from .routers import router

# sess_patterns = patterns('',
#     url(r'^/?$', views.session, name='view'),
# )
# 
# sbj_patterns = patterns('',
#     url(r'^/?$', views.subject, name='index'),
#     url(r'^/session/(?P<session_number>\d+)',
#         include(sess_patterns, namespace='session')),
# )
# 
# app_patterns = patterns('',
#     url(r'^/?$', SubjectList.as_view(), name='home'),
#     url(r'^/(?P<collection_name>\w+)/(?P<subject_number>\d+)',
#         include(sbj_patterns, namespace='subject')),
#     url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
#     url(r'^/help/?$', views.help, name='help'),
# )

urlpatterns = patterns('',
    # The qiprofile URLs.
    url(r'', include(router.urls, namespace='qiprofile')),
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
