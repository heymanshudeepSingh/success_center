"""
Urls for CAE Tools app.
"""

from django.urls import path

from . import views


app_name = 'cae_tools'
urlpatterns = [
    # CSS Example urls.
    path('css_examples/alerts', views.css_alerts, name='css_alerts'),
    path('css_examples/articles', views.css_articles, name='css_articles'),
    path('css_examples/buttons', views.css_buttons, name='css_buttons'),
    path('css_examples/forms', views.css_forms, name='css_forms'),
    path('css_examples/nav', views.css_nav, name='css_nav'),
    path('css_examples/page_tabbing', views.css_page_tabbing, name='css_page_tabbing'),
    path('css_examples/panels', views.css_panels, name='css_panels'),
    path('css_examples/status_messages', views.css_status_messages, name='css_status_messages'),
    path('css_examples/tables', views.css_tables, name='css_tables'),
    path('css_examples/text_highlighting', views.css_text_highlighting, name='css_text_highlighting'),
    path('css_examples/', views.css_examples, name='css_examples'),

    # Color Tool urls.
    path('color/', views.color_tool, name='color_tool'),

    # Home url.
    path('', views.index, name='index'),
]
