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

    # Custom Workspace Logic Documentation.
    path('documentation/css/', views.docs_css, name='documentation_css'),
    path('documentation/general_setup/', views.docs_general_setup, name='documentation_general_setup'),
    path('documentation/javascript/', views.docs_javascript, name='documentation_javascript'),

    # path('documentation/ldap/', views.docs_ldap, name='documentation_ldap'),
    path('documentation/ldap/setup/', views.docs_ldap_setup, name='documentation_ldap_setup'),
    path('documentation/ldap/auth_backends/', views.docs_ldap_auth_backends, name='documentation_ldap_auth_backends'),
    path('documentation/ldap/utility_connectors/', views.docs_ldap_utility_connectors, name='documentation_ldap_utility_connectors'),

    path('documentation/middleware/', views.docs_middlware, name='documentation_middleware'),
    path('documentation/models/', views.docs_middlware, name='documentation_models'),
    path('documentation/seeds_and_fixtures/', views.docs_seeds_and_fixtures, name='documentation_seeds_and_fixtures'),

    # path('documentation/settings/', views.docs_settings, name='documentation_settings'),
    path('documentation/settings/organization/', views.docs_settings_organization, name='documentation_settings_organization'),
    path('documentation/settings/local_environment/', views.docs_settings_local_environment, name='documentation_settings_local_environment'),
    path('documentation/settings/dev_password/', views.docs_settings_dev_password, name='documentation_settings_dev_password'),
    path('documentation/settings/logging/', views.docs_settings_logging, name='documentation_settings_logging'),

    path('documentation/subprojects/', views.docs_subprojects, name='documentation_subprojects'),
    path('documentation/templates/', views.docs_templates, name='documentation_templates'),
    path('documentation/tests/', views.docs_tests, name='documentation_tests'),
    path('documentation/views/', views.docs_views, name='documentation_views'),
    path('documentation/', views.documentation, name='documentation'),

    # Color Tool urls.
    path('color/', views.color_tool, name='color_tool'),

    # Home url.
    path('', views.index, name='index'),
]
