"""
Urls for CAE Tools app.
"""

from django.urls import path

from . import views


app_name = 'cae_tools'
urlpatterns = [
    # CSS Example urls.
    path('documentation/css_examples/alerts', views.css_alerts, name='css_alerts'),
    path('documentation/css_examples/articles', views.css_articles, name='css_articles'),
    path('documentation/css_examples/buttons', views.css_buttons, name='css_buttons'),
    path('documentation/css_examples/forms', views.css_forms, name='css_forms_base'),
    path('documentation/css_examples/forms/default_fields', views.css_forms_default_fields, name='css_forms_default_fields'),
    path('documentation/css_examples/forms/custom_fields', views.css_forms_custom_fields, name='css_forms_custom_fields'),
    path('documentation/css_examples/forms/other', views.css_forms_misc, name='css_forms_misc'),
    path('documentation/css_examples/nav', views.css_nav, name='css_nav'),
    path('documentation/css_examples/page_tabbing', views.css_page_tabbing, name='css_page_tabbing'),
    path('documentation/css_examples/panels', views.css_panels, name='css_panels'),
    path('documentation/css_examples/status_messages', views.css_status_messages, name='css_status_messages'),
    path('documentation/css_examples/tables', views.css_tables, name='css_tables'),
    path('documentation/css_examples/text_highlighting', views.css_text_highlighting, name='css_text_highlighting'),
    path('documentation/css_examples/', views.css_examples, name='css_examples'),

    # Color Tool urls.
    path('color/', views.color_tool, name='color_tool'),

    # Home url.
    path('', views.index, name='index'),
]
