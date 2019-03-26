"""
Urls for CAE_Home App.
"""

from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls import url

from . import views


# Error url handling.
handler400 = views.handler400   # Bad/suspicious request.
handler403 = views.handler403   # Permission denied.
handler404 = views.handler404   # Page not found.
handler500 = views.handler500   # Server error.


# General url handling.
app_name = 'cae_home'
urlpatterns = [

    # Auth pages.
    url(r'^user/login/$', views.login, name='login'),
    url(r'^user/login_redirect/$', views.login_redirect, name='login_redirect'),
    url(r'^user/logout/$', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # CAE Home/Index page.
    url(r'^$', views.index, name='index'),
]


# Debug only urls.
if settings.DEV_URLS:
    urlpatterns += [
        # Error page test views.
        url(r'^404/$', views.handler400, name='error_404'),

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
