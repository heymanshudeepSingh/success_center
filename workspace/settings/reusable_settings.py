"""
Reusable settings for project.
May be imported by multiple files.
"""

# System Imports.
import os, sys


# Get base directory.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
ERR_TEMPLATE_DIR = os.path.join(BASE_DIR, 'cae_home/errors/')


def get_dynamic_app_path(app_file_name):
    """
    Call from app "apps.py" config file to get properly formatted config path.
    :param app_file_name: The "__file__" parameter of config.
    :return: Properly formatted config path.
    """
    # First get full project and app directory paths.
    app_folder_path = os.path.dirname(os.path.realpath(app_file_name))
    project_folder_path = os.path.dirname(app_folder_path)

    # Parse to get the relevant folder names.
    app_folder_name = os.path.basename(app_folder_path)
    project_folder_name = os.path.basename(project_folder_path)

    # Return properly formatted string.
    return 'apps.{0}.{1}'.format(project_folder_name, app_folder_name)


def debug_print(*args, **kwargs):
    """
    Method to print debug statements if using essential manage.py commands.
    :param args:
    :param kwargs:
    :return:
    """
    runserver_true = len(sys.argv) > 1 and sys.argv[1] in ['runserver', 'test', 'migrate', 'makemigrations']

    if runserver_true:
        print(*args, **kwargs)


"""
    Dev Mode and Debug.
        DEV_MODE is true if a file named "DEBUG" exists in the base project directory.
        This is done to easily separate production mode and development mode.
        Site will default to production unless debug file is explicitly created.
"""
DEBUG_FILE = os.path.join(BASE_DIR, 'DEBUG')
DEV_MODE = os.path.exists(DEBUG_FILE)
DEBUG = DEV_MODE
# debug_print("DEBUG = " + str(DEBUG))


class ConsoleColors:
    """
    Escape codes to change console output colors when debugging.

    Full explanation can be found at http://ozzmaker.com/add-colour-to-text-in-python/ and
    https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
    """
    reset = '\033[0m'
    bold_red = '\033[1;31m'
    bold_yellow = '\033[1;33m'
    bold_blue = '\033[1;34m'


# Define helper user-value lists, mostly for testing purposes.
CAE_CENTER_TEST_USERS = [
    'cae_building_coordinator',
    'cae_director',
    'cae_admin',
    'cae_attendant',
    'cae_programmer',
    'cae_admin_ga',
    'cae_programmer_ga',
]
CAE_CENTER_GROUPS = [
    'CAE Building Coordinator',
    'CAE Director',
    'CAE Admin GA',
    'CAE Programmer GA',
    'CAE Admin',
    'CAE Attendant',
    'CAE Programmer',
]
CAE_ADMIN_GROUPS = [
    'CAE Director',
    'CAE Admin GA',
    'CAE Programmer GA',
]
SUCCESS_CENTER_TEST_USERS = ['step_admin', 'step_employee']
SUCCESS_CENTER_GROUPS = ['STEP Admin', 'STEP Employee']
GRAD_APPS_TEST_USERS = ['grad_apps_admin', 'grad_apps_committee_member']
GRAD_APPS_USERS = ['Grad Apps Admin', 'Grad Apps Committee Member']


# Predefined Email Sections.
cae_email_header = """
<span style="font-size:8pt; color: #757B80;">
This is an automatically generated email. Please do not respond to this email.<br>
If you have any questions or concerns, please contact the CAE Center.<br>
</span>
"""

cae_email_footer = """
<span style="font-size:8pt; font-weight: bold;">
CAE Center<br>
College of Engineering and Applied Sciences<br>
Western Michigan University<br>
(269) 276-3283<br>
ceas_cae@wmich.edu<br>
</span>
"""
