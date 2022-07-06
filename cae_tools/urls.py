"""
Urls for CAE Tools app.
"""

from django.urls import path

from . import views


app_name = 'cae_tools'
urlpatterns = [
    # LDAP Utility Pages
    path('padl/search/', views.ldap_utility, name='padl_utility'),
    path('password_reset/', views.cae_password_reset, name='password_reset'),
    path('reset_password/', views.cae_password_reset, name='reset_password'),

    # Color Tool urls.
    path('color/', views.color_tool, name='color_tool'),
]
