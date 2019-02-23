"""
Urls for CAE Tools app.
"""

from django.conf.urls import url

from . import views


app_name = 'cae_tools'
urlpatterns = [
    url(r'color/$', views.color_tool, name='color_tool'),
]
