"""
Urls for CAE Tools app.
"""

from django.conf.urls import url

from . import views


app_name = 'cae_tools'
urlpatterns = [
    url(r'css_examples/$', views.css_examples, name='css_examples'),
    url(r'color/$', views.color_tool, name='color_tool'),
    url(r'$', views.index, name='index'),
]
