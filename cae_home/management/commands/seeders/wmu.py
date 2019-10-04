"""
Seeder for "WMU" related Core Models.

Note that seeder methods will always call fixture methods first. Then attempt seeding afterwards.
"""

# System Imports.
from sys import stdout

# User Class Imports.
from cae_home.management.commands.fixtures import wmu as wmu_fixtures


def generate_model_seeds(style, model_count):
    """
    Calls individual seeder methods.
    """
    stdout.write(style.HTTP_NOT_MODIFIED('SEEDING WMU Model Group.\n'))
    create_room_types(style)
    create_departments(style)
    create_rooms(style)
    create_majors(style)
    create_semester_dates(style)


def create_room_types(style):
    """
    Create Room Type models.
    """
    # Load preset fixtures.
    wmu_fixtures.create_room_types(style)

    stdout.write('Populated ' + style.SQL_FIELD('Room Type') + ' models.\n')


def create_departments(style):
    """
    Create Department models.
    """
    # Load preset fixtures.
    wmu_fixtures.create_departments(style)

    stdout.write('Populated ' + style.SQL_FIELD('Department') + ' models.\n')


def create_rooms(style):
    """
    Create Room models.
    """
    # Load preset fixtures.
    wmu_fixtures.create_rooms(style)

    stdout.write('Populated ' + style.SQL_FIELD('Room') + ' models.\n')


def create_majors(style):
    """
    Create Major models.
    """
    # Load preset fixtures.
    wmu_fixtures.create_majors(style)

    stdout.write('Populated ' + style.SQL_FIELD('Major') + ' models.\n')


def create_semester_dates(style):
    """
    Create Semester Date models.
    """
    # Load preset fixtures.
    wmu_fixtures.create_semester_dates(style)

    stdout.write('Populated ' + style.SQL_FIELD('Semester Date') + ' models.\n')
