"""
Urls for CAE Tools app.
"""

from django.urls import path

from . import views


app_name = 'cae_tools'
urlpatterns = [
    # LDAP Utility Pages.
    path('padl/search/', views.ldap_utility, name='padl_utility'),
    path('password_reset/', views.cae_password_reset, name='password_reset'),
    path('reset_password/', views.cae_password_reset, name='reset_password'),

    # Color Tool urls.
    path('color/', views.color_tool, name='color_tool'),

    # Api urls.
    path('api/wmu_user/', views.get_wmu_user, name='api_wmu_user'),
    path('api/department/', views.get_department, name='api_department'),
    path('api/room_type/', views.get_room_type, name='api_room_type'),
    path('api/room/', views.get_room, name='api_room'),
    path('api/major/', views.get_major, name='api_major'),
    path('api/class/', views.get_class, name='api_class'),
    path('api/semester/', views.get_semester, name='api_semester'),
]
