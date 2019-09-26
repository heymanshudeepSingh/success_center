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
    create_room_types(style)
    create_departments(style)
    create_rooms(style)
    create_majors(style)
    create_semester_dates(style)


def create_room_types(style):
    """
    Imports fixtures for Room Type models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'full_models/room_types')

    stdout.write('Imported fixtures for ' + style.SQL_FIELD('Room Type') + ' models.\n')


def create_departments(style):
    """
    Imports fixtures for Department models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'full_models/departments')

    stdout.write('Imported fixtures for ' + style.SQL_FIELD('Department') + ' models.\n')


def create_rooms(style):
    """
    Imports fixtures for Room models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'full_models/rooms')

    stdout.write('Imported fixtures for ' + style.SQL_FIELD('Room') + ' models.\n')


def create_majors(style):
    """
    Imports fixtures for Major models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'full_models/majors')

    stdout.write('Imported fixtures for ' + style.SQL_FIELD('Major') + ' models.\n')


def create_semester_dates(style):
    """
    Imports fixtures for Semester Date models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'full_models/semester_dates')

    stdout.write('Imported fixtures for ' + style.SQL_FIELD('Semester Date') + ' models.\n')
