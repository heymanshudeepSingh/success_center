"""
Urls for CAE Tools app.
"""

from django.urls import path

from . import views


app_name = 'cae_tools'
urlpatterns = [
    path('css_examples/', views.css_examples, name='css_examples'),
    path('color/', views.color_tool, name='color_tool'),
    path('', views.index, name='index'),
]
