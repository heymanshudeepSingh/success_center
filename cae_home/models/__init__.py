"""
Models for CAE Home app.

Models here should be "core" models which have overlap in various subprojects.
If a model only applies to a single project, then it should be defined within that project.
"""

# Models related to WMU in general.
from .wmu import Department
from .wmu import RoomType
from .wmu import Room
from .wmu import Major
from .wmu import Semester

# Models related to user-login accounts.
from .user import User
from .user import GroupMembership
from .user import UserIntermediary
from .user import WmuUser
from .user import Profile
from .user import Address
from .user import SiteTheme
from .user import WmuUserMajorRelationship

# Models related to the CAE Center.
from .cae import Asset
from .cae import Software
from .cae import SoftwareDetail
