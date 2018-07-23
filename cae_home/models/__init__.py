"""
Models for CAE Home app.

Models here should be "core" models which have overlap in various subprojects.
If a model only applies to a single project, then it should be defined within that project.
"""

# Models related to user-login accounts.
from .user import User
from .user import Profile
from .user import Address
from .user import PhoneNumber

# Models related to WMU in general.
from .wmu import Department
from .wmu import RoomType
from .wmu import Room
from .wmu import Major
from .wmu import Student
from .wmu import SemesterDate

# Models related to the CAE Center.
from .cae import Asset
