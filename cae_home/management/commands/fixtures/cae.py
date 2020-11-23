"""
Fixture Imports for "CAE Center" related Core Models.
"""

# System Imports.
from django.core.management import call_command
from sys import stdout


def import_model_fixtures(style):
    """
    Calls individual fixture methods.
    """
    stdout.write(style.HTTP_NOT_MODIFIED('IMPORTING FIXTURES for User Model Group.\n'))
    # create_assets(style)
    create_software(style)
    create_software_detail(style)


def create_assets(style, display_output=False):
    """
    Imports fixtures for Asset models.
    """
    # Nothing here yet.
    pass


def create_software(style, display_output=False):
    """
    Imports fixtures for Software models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'production_models/software')

    if display_output and style is not None:
        stdout.write('Imported fixtures for ' + style.SQL_FIELD('Software') + ' models.\n')


def create_software_detail(style, display_output=False):
    """
    Imports fixtures for Software Detail models.
    """
    # Load preset fixtures.
    call_command('loaddata', 'production_models/software_detail')

    if display_output and style is not None:
        stdout.write('Imported fixtures for ' + style.SQL_FIELD('Software Detail') + ' models.\n')
