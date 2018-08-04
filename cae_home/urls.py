"""
Urls for CAE_Home App.
"""

from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls import url

from . import views


app_name = 'cae_home'
urlpatterns = [

    # Auth pages.
    url(r'^user/login/$', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    url(r'^user/logout/$', auth_views.logout, name='logout', kwargs={'next_page': '/',}),

    # CAE Home/Index page.
    url(r'^$', views.index, name='index'),
]


# Debug only urls.
if settings.DEBUG:
    urlpatterns += [
        # "WMU Clone" test page. Only use for layout and css development.
        url(r'^wmu/$', views.wmu_test, name='wmu_test'),
    ]
