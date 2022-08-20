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
    create_semesters(style, display_output=True)


def create_wmu_classes(style, display_output=False):
    """
    Imports fixtures for Wmu Class models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'production_models/wmu_classes')

    if display_output and style is not None:
        stdout.write('Imported fixtures for ' + style.SQL_FIELD('Wmu class') + ' models.\n')


def create_room_types(style, display_output=False):
    """
    Imports fixtures for Room Type models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'production_models/room_types')

    if display_output and style is not None:
        stdout.write('Imported fixtures for ' + style.SQL_FIELD('Room Type') + ' models.\n')


def create_departments(style, display_output=False):
    """
    Imports fixtures for Department models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'production_models/departments')

    if display_output and style is not None:
        stdout.write('Imported fixtures for ' + style.SQL_FIELD('Department') + ' models.\n')


def create_rooms(style, display_output=False):
    """
    Imports fixtures for Room models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'production_models/rooms')

    if display_output and style is not None:
        stdout.write('Imported fixtures for ' + style.SQL_FIELD('Room') + ' models.\n')


def create_majors(style, display_output=False):
    """
    Imports fixtures for Major models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'production_models/majors')

    if display_output and style is not None:
        stdout.write('Imported fixtures for ' + style.SQL_FIELD('Major') + ' models.\n')


def create_semesters(style, display_output=False):
    """
    Imports fixtures for Semester models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'production_models/semesters')

    if display_output and style is not None:
        stdout.write('Imported fixtures for ' + style.SQL_FIELD('Semester') + ' models.\n')
