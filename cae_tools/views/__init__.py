"""
Views for CAE Tools app.

Split up into separate files for organization. Imported here.
"""

# Api Views.
from .api_views import (
    get_department,
    get_major,
    get_room_type,
    get_room,
    get_class,
    get_semester,
    get_wmu_user,
)

# Documentation Views.
from .documentation_views import *

# Tool Views.
from .tools import color_tool

# Misc Views.
from .misc import index
from .misc import documentation
from .ldap import ldap_utility
from .ldap import cae_password_reset
