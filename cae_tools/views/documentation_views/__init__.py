"""
Views for CAE Tools app.

Split up into separate files for organization. Documentation views are imported here.
"""

# Custom "CSS" Logic Documentation.
from .css import docs_css

# CSS Example Documentation.
from .css_examples import css_examples
from .css_examples import css_alerts
from .css_examples import css_articles
from .css_examples import css_buttons
from .css_examples import css_forms
from .css_examples import css_forms_default_fields
from .css_examples import css_forms_custom_fields
from .css_examples import css_forms_misc
from .css_examples import css_nav
from .css_examples import css_page_tabbing
from .css_examples import css_panels
from .css_examples import css_status_messages
from .css_examples import css_tables
from .css_examples import css_text_highlighting

# Custom "General Setup" Logic Documentation.
from .general_setup import docs_general_setup

# Custom "JavaScript" Logic Documentation.
from .javascript import docs_javascript

# Custom "LDAP" Logic Documentation.
from .ldap import docs_ldap
from .ldap import docs_ldap_setup
from .ldap import docs_ldap_auth_backends
from .ldap import docs_ldap_utility_connectors

# Custom "Middleware" Logic Documentation.
from .middleware import docs_middlware

# Custom "Models" Logic Documentation.
from .models import docs_models

# Custom "Seeds and Fixtures" Logic Documentation.
from .seeds_and_fixtures import docs_seeds_and_fixtures

# Custom "Settings" Logic Documentation.
from .settings import docs_settings

# Custom "Sub Project" Logic Documentation.
from .subprojects import docs_subprojects

# Custom "Templates" Logic Documentation.
from .templates import docs_templates

# Custom "Tests" Logic Documentation.
from .tests import docs_tests

# Custom "Views" Logic Documentation.
from .views import docs_views
