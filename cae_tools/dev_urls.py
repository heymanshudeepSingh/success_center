"""
Urls for CAE Tools app.
"""

# System Imports.
from django.urls import path

# User Imports.
from . import views


app_name = 'dev'
urlpatterns = [

    # CSS Example urls.
    path('documentation/css_examples/alerts', views.css_alerts, name='css_alerts'),
    path('documentation/css_examples/articles', views.css_articles, name='css_articles'),
    path('documentation/css_examples/buttons', views.css_buttons, name='css_buttons'),
    path('documentation/css_examples/cards', views.css_cards, name='css_cards'),
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
    path('documentation/css_examples/grad_apps_misc', views.css_grad_apps_misc, name='css_grad_apps_misc'),
    path('documentation/css_examples/', views.css_examples, name='css_examples'),

    # CSS documentation urls.
    path('documentation/css/general_logic/', views.docs_css_general_logic, name='documentation_css_general'),
    path('documentation/css/using_flexbox/', views.docs_css_using_flexbox, name='documentation_css_flexbox'),

    # General/Introduction documentation urls.
    path('documentation/intro/introduction', views.docs_intro, name='documentation_introduction'),
    path('documentation/intro/first_steps', views.docs_intro_first_steps, name='documentation_intro_first_steps'),
    path('documentation/intro/helper_scripts', views.docs_intro_helper_scripts, name='documentation_intro_helper_scripts'),
    path('documentation/intro/setup', views.docs_intro_setup, name='documentation_intro_setup'),
    path('documentation/intro/managepy', views.docs_intro_managepy, name='documentation_intro_managepy'),
    path('documentation/intro/virtual_environments', views.docs_intro_virtual_environments, name='documentation_intro_virtual_environments'),

    # JavaScript documentation urls.
    path('documentation/javascript/passing_variables/', views.docs_javascript_passing_variables, name='documentation_javascript_passing_variables'),
    path('documentation/javascript/libraries/', views.docs_javascript_libraries, name='documentation_javascript_libraries'),

    # Ldap Documentation urls.
    path('documentation/ldap/setup/', views.docs_ldap_setup, name='documentation_ldap_setup'),
    path('documentation/ldap/auth_backends/', views.docs_ldap_auth_backends, name='documentation_ldap_auth_backends'),
    path('documentation/ldap/utility_connectors/', views.docs_ldap_utility_connectors, name='documentation_ldap_utility_connectors'),

    # Custom Workspace Logic Documentation.
    path('documentation/middleware/', views.docs_middlware, name='documentation_middleware'),
    path('documentation/models/', views.docs_middlware, name='documentation_models'),
    path('documentation/seeds_and_fixtures/', views.docs_seeds_and_fixtures, name='documentation_seeds_and_fixtures'),

    # Settings documentation urls.
    path('documentation/settings/organization/', views.docs_settings_organization, name='documentation_settings_organization'),
    path('documentation/settings/local_environment/', views.docs_settings_local_environment, name='documentation_settings_local_environment'),
    path('documentation/settings/dev_password/', views.docs_settings_dev_password, name='documentation_settings_dev_password'),
    path('documentation/settings/logging/', views.docs_settings_logging, name='documentation_settings_logging'),

    # Custom Workspace Logic Documentation.
    path('documentation/subprojects/', views.docs_subprojects, name='documentation_subprojects'),
    path('documentation/templates/', views.docs_templates, name='documentation_templates'),

    # Testing documentation urls.
    path('documentation/testing/running_tests/', views.docs_running_tests, name='documentation_testing_running_tests'),
    path('documentation/testing/base_test_case/', views.docs_base_test_case, name='documentation_testing_base_test_case'),
    path('documentation/testing/integration_test_case/', views.docs_integration_test_case, name='documentation_testing_integration_test_case'),
    path('documentation/testing/live_server_test_case/', views.docs_live_server_test_case, name='documentation_testing_live_server_test_case'),

    # Custom Workspace Logic Documentation.
    path('documentation/views/', views.docs_views, name='documentation_views'),
    path('documentation/', views.documentation, name='documentation'),

    # Home url.
    path('', views.index, name='index'),
]
