"""
Urls for CAE Home app.
"""

# System Imports.
from django.conf import settings
from django.conf.urls import url
from django.views.generic import TemplateView

# User Class Imports.
from . import views


# General url handling.
app_name = 'cae_home'
urlpatterns = [
    # Auth pages.
    url(r'^user/login/$', views.login, name='login'),
    url(r'^user/login_redirect/$', views.login_redirect, name='login_redirect'),
    url(r'^user/logout/$', views.logout, name='logout'),

    # Info pages.
    url(r'^info/schedules/$', views.info_schedules, name='info_schedules'),
    url(r'^info/servers/$', views.info_servers, name='info_servers'),
    url(r'^info/software/$', views.info_software, name='info_software'),

    # User pages.
    url(r'^user/edit/(?P<slug>[\w-]+)/$', views.user_edit, name='user_edit'),
    url(r'^user/helpful_resources/$', views.helpful_resources, name='helpful_resources'),

    # Error page test views.
    url(r'^error/400/$', views.test_400_error, name='error_400'),
    url(r'^error/403/$', views.test_403_error, name='error_403'),
    # url(r'^error/404/$', views.test_404_error, name='error_404'),
    url(r'^error/500/$', views.test_500_error, name='error_500'),

    # CAE Home/Index page.
    url(r'^$', views.index, name='index'),
]


# Debug only urls.
if settings.DEV_URLS:
    urlpatterns += [
        # Internal site ("CAE Home") test page(s).
        # Used for layout format and general testing of "internal facing" views.
        url(r'^cae/$', views.internal_dev_index, name='internal_dev_index'),

        # External site ("WMU Clone") test page(s).
        # Used for layout format and general testing of "external facing" views.
        url(r'^wmu/$', views.external_dev_index, name='external_dev_index'),

        # Email Testing.
        url(r'^test_single_email/$', views.test_single_email, name='test_single_email'),
        url(r'^test_mass_email/$', views.test_mass_email, name='test_mass_email'),
    ]
