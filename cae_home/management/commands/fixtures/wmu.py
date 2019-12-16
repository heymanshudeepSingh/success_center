"""
Fixture imports for "WMU" related Core Models.
"""

# System Imports.
from django.core.management import call_command
from sys import stdout


def import_model_fixtures(style):
    """
    Calls individual fixture methods.
    """
    stdout.write(style.HTTP_NOT_MODIFIED('IMPORTING FIXTURES For WMU Model Group.\n'))
    create_room_types(style, display_output=True)
    create_departments(style, display_output=True)
    create_rooms(style, display_output=True)
    create_majors(style, display_output=True)
    create_semester_dates(style, display_output=True)


def create_room_types(style, display_output=False):
    """
    Imports fixtures for Room Type models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'full_models/room_types')

    if display_output and style is not None:
        stdout.write('Imported fixtures for ' + style.SQL_FIELD('Room Type') + ' models.\n')


def create_departments(style, display_output=False):
    """
    Imports fixtures for Department models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'full_models/departments')

    if display_output and style is not None:
        stdout.write('Imported fixtures for ' + style.SQL_FIELD('Department') + ' models.\n')


def create_rooms(style, display_output=False):
    """
    Imports fixtures for Room models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'full_models/rooms')

    if display_output and style is not None:
        stdout.write('Imported fixtures for ' + style.SQL_FIELD('Room') + ' models.\n')


def create_majors(style, display_output=False):
    """
    Imports fixtures for Major models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'full_models/majors')

    if display_output and style is not None:
        stdout.write('Imported fixtures for ' + style.SQL_FIELD('Major') + ' models.\n')


def create_semester_dates(style, display_output=False):
    """
    Imports fixtures for Semester Date models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'full_models/semester_dates')

    if display_output and style is not None:
        stdout.write('Imported fixtures for ' + style.SQL_FIELD('Semester Date') + ' models.\n')
