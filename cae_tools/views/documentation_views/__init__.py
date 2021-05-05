"""
Views for CAE Tools app.

Split up into separate files for organization. Documentation views are imported here.
"""

# Custom "CSS" Logic Documentation.
from .css import docs_css

# CSS Example Documentation.
from .css_examples import (
    css_examples,
    css_alerts,
    css_articles,
    css_buttons,
    css_forms,
    css_forms_default_fields,
    css_forms_custom_fields,
    css_forms_misc,
    css_nav,
    css_page_tabbing,
    css_panels,
    css_status_messages,
    css_tables,
    css_text_highlighting,
)


# Custom "General Setup" Logic Documentation.
from .general_setup import docs_general_setup

# Custom "JavaScript" Logic Documentation.
from .javascript import (
    docs_javascript,
    docs_javascript_passing_variables,
    docs_javascript_libraries,
)


# Custom "LDAP" Logic Documentation.
from .ldap import (
    docs_ldap,
    docs_ldap_setup,
    docs_ldap_auth_backends,
    docs_ldap_utility_connectors,
)


# Custom "Middleware" Logic Documentation.
from .middleware import docs_middlware

# Custom "Models" Logic Documentation.
from .models import docs_models

# Custom "Seeds and Fixtures" Logic Documentation.
from .seeds_and_fixtures import docs_seeds_and_fixtures

# Custom "Settings" Logic Documentation.
from .settings import (
    docs_settings,
    docs_settings_organization,
    docs_settings_local_environment,
    docs_settings_dev_password,
    docs_settings_logging,
)


# Custom "Sub Project" Logic Documentation.
from .subprojects import docs_subprojects

# Custom "Templates" Logic Documentation.
from .templates import docs_templates

# Custom "Testing" Logic Documentation.
from .tests import (
    docs_running_tests,
    docs_base_test_case,
    docs_integration_test_case,
    docs_live_server_test_case,
)

# Custom "Views" Logic Documentation.
from .views import docs_views
