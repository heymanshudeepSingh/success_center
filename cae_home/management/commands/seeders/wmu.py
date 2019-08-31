"""
Seeder for "WMU" related Core Models.
"""

# System Imports.
from django.core.management import call_command
from sys import stdout


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
    # Load preset fixtures. No need to create random models.
    call_command('loaddata', 'full_models/room_types')

    stdout.write('Populated ' + style.SQL_FIELD('Room Type') + ' models.\n')


def create_departments(style):
    """
    Create Department models.
    """
    # Load preset fixtures. No need to create random models.
    call_command('loaddata', 'full_models/departments')

    stdout.write('Populated ' + style.SQL_FIELD('Department') + ' models.\n')


def create_rooms(style):
    """
    Create Room models.
    """
    # Load preset fixtures. No need to create random models.
    call_command('loaddata', 'full_models/rooms')

    stdout.write('Populated ' + style.SQL_FIELD('Room') + ' models.\n')


def create_majors(style):
    """
    Create Major models.
    """
    # Load preset fixtures. No need to create random models.
    call_command('loaddata', 'full_models/majors')

    stdout.write('Populated ' + style.SQL_FIELD('Major') + ' models.\n')


def create_semester_dates(style):
    """
    Create Semester Date models.
    """
    # Load preset fixtures. No need to create random models.
    call_command('loaddata', 'full_models/semester_dates')

    stdout.write('Populated ' + style.SQL_FIELD('Semester Date') + ' models.\n')
