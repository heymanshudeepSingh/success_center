"""
Urls for CAE_Home App.
"""

from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views


# General url handling.
app_name = 'cae_home'
urlpatterns = [

    # Auth pages.
    url(r'^user/login/$', views.login, name='login'),
    url(r'^user/login_redirect/$', views.login_redirect, name='login_redirect'),
    url(r'^user/logout/$', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    url(r'^user/edit/(?P<slug>[\w-]+)/$', views.user_edit, name='user_edit'),

    # CAE Home/Index page.
    url(r'^$', views.index, name='index'),
]


# Debug only urls.
if settings.DEV_URLS:
    urlpatterns += [
        # Error page test views.
        url(r'^error/400/$', TemplateView.as_view(template_name='cae_home/errors/400.html'), name='error_400'),
        url(r'^error/403/$', TemplateView.as_view(template_name='cae_home/errors/403.html'), name='error_403'),
        url(r'^error/404/$', TemplateView.as_view(template_name='cae_home/errors/404.html'), name='error_404'),
        url(r'^error/500/$', TemplateView.as_view(template_name='cae_home/errors/500.html'), name='error_500'),

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
