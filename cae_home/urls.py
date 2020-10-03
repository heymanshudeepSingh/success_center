"""
Urls for CAE Home app.
"""

# System Imports.
from django.conf import settings
from django.urls import path

# User Class Imports.
from . import views


# General url handling.
app_name = 'cae_home'
urlpatterns = [
    # Auth pages.
    path('user/login/', views.login, name='login'),
    path('user/login_redirect/', views.login_redirect, name='login_redirect'),
    path('user/logout/', views.logout, name='logout'),

    # Info pages.
    path('info/schedules/', views.info_schedules, name='info_schedules'),
    path('info/servers/', views.info_servers, name='info_servers'),
    path('info/software/', views.info_software, name='info_software'),

    # User pages.
    path('user/edit/<slug>/', views.user_edit, name='user_edit'),
    path('user/helpful_resources/', views.helpful_resources, name='helpful_resources'),

    # Error page test views.
    path('error/400/', views.test_400_error, name='error_400'),
    path('error/403/', views.test_403_error, name='error_403'),
    # path('error/404/', views.test_404_error, name='error_404'),
    path('error/500/', views.test_500_error, name='error_500'),

    # Other views.
    path('user/get_user/login/', views.GetLoginUser.as_view(), name='get_login_user'),
    path('user/get_user/wmu/', views.GetWmuUser.as_view(), name='get_wmu_user'),

    # CAE Home/Index page.
    path('', views.index, name='index'),
]


# Debug only urls.
if settings.DEV_URLS:
    urlpatterns += [
        # Internal site ("CAE Home") test page(s).
        # Used for layout format and general testing of "internal facing" views.
        path('cae/', views.internal_dev_index, name='internal_dev_index'),

        # External site ("WMU Clone") test page(s).
        # Used for layout format and general testing of "external facing" views.
        path('wmu/', views.external_dev_index, name='external_dev_index'),

        # Email Testing.
        path('test_single_email/', views.test_single_email, name='test_single_email'),
        path('test_mass_email/', views.test_mass_email, name='test_mass_email'),
    ]
