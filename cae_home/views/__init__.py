"""
Views for CAE Home app.

Split up into separate files for organization. Imported here.
"""

# Debug views.
from .debug_views import (
    index,
    internal_dev_index,
    external_dev_index,
    test_400_error,
    test_403_error,
    test_500_error,
    test_single_email,
)

# DjangoRest views.
from .django_rest_views import DepartmentViewSet

# Form views.
from .user_management_views import (
    UserDetails,
    user_edit,
    change_password,
    manage_user_access_groups,
)

# Login views.
from .auth_views import (
    login,
    login_redirect,
    logout,
)

# Misc views.
from .misc_views import (
    handler400,
    handler403,
    handler404,
    handler500,
    info_schedules,
    info_servers,
    info_software,
    helpful_resources,
    GetLoginUserExample,
    GetWmuUserExample,
)
