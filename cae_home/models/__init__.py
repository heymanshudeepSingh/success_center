"""
Models for CAE Home app.

Models here should be "core" models which have overlap in various subprojects.
If a model only applies to a single project, then it should be defined within that project.
"""

# Custom model fields.
from .fields import (
    CodeField,
)

# Models related to WMU in general.
from .wmu import (
    Department,
    RoomType,
    Room,
    Major,
    WmuClass,
    Semester,
    StudentHistory,
)

# Models related to user-login accounts.
from .user import (
    User,
    GroupMembership,
    UserIntermediary,
    WmuUser,
    Profile,
    Address,
    SiteTheme,
    WmuUserMajorRelationship,
)

# Models related to the CAE Center.
from .cae import (
    Asset,
    Software,
    SoftwareDetail,
)
