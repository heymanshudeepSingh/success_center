"""
Models for CAE Home app.

Models here should be "core" models which have overlap in various subprojects.
If a model only applies to a single project, then it should be defined within that project.
"""

# CAE Center specific User Group names.
cae_employee_groups = [
    'CAE Director',
    'CAE Building Coordinator',
    'CAE Attendant',
    'CAE Admin',
    'CAE Programmer',
]

# STEP specific User Group names.
step_employee_groups = [
    'STEP Admin',
    'STEP Employee',
]

# Debug views.
from .debug_views import index
from .debug_views import internal_dev_index
from .debug_views import external_dev_index
from .debug_views import test_400_error
from .debug_views import test_403_error
from .debug_views import test_500_error
from .debug_views import test_single_email
from .debug_views import test_mass_email

# DjangoRest views.
from .django_rest_views import DepartmentViewSet

# Form views.
from .form_views import user_edit

# Login views.
from .auth_views import login
from .auth_views import login_redirect
from .auth_views import logout

# Misc views.
from .misc_views import handler400
from .misc_views import handler403
from .misc_views import handler404
from .misc_views import handler500
from .misc_views import info_schedules
from .misc_views import info_servers
from .misc_views import info_software
from .misc_views import helpful_resources
from .misc_views import get_or_create_login_user_model
from .misc_views import get_or_create_wmu_user_model
