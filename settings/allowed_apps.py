"""
Manages and auto-installs apps for project.
"""

# User Class Imports.
from settings.reusable_settings import *


APP_DIR = os.path.join(BASE_DIR, 'apps')

debug_print('')


# Django base apps, any 3rd party add-on apps, and CAE_Home app.
# All other CAE Apps should be defined under the "Allowed_CAE_Apps" setting.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'cae_home.apps.CaeHomeConfig',
]


# List of allowed apps to automatically install.
# Formatted as a dictionary of sub-dictionary values.
ALLOWED_CAE_APPS = {
    
}


# Automatically populated for automatic url generation on home page. Do not edit.
INSTALLED_CAE_APPS = {}

# Logic to automatically install a given allowed app, if found.
# First iterate through list of all project folders within the apps folder.
debug_print('Automatically Installed Apps:')
project_folder_list = [x for x in os.listdir(APP_DIR) if os.path.isdir(os.path.join(APP_DIR, x))]
excluded_project_list = []
for project_name in project_folder_list:

    # Check that project is defined through settings.
    if project_name in ALLOWED_CAE_APPS.keys():
        debug_print('   Included Project{0}'.format(project_name))

        # Grab all app folders within given project.
        project_folder = os.path.join(APP_DIR, project_name)
        app_folder_list = [
            x for x in os.listdir(project_folder)
            if os.path.isdir(os.path.join(project_folder, x)) and not x.startswith('.git')
        ]
        excluded_app_list = []

        # Iterate through project apps.
        for app_name in app_folder_list:

            # Check that app is defined through settings.
            if app_name in ALLOWED_CAE_APPS[project_name]['related_apps']:
                debug_print('      Included App {0}'.format(app_name))
            else:
                # App not allowed through settings.
                excluded_app_list.append(app_name)

        for app_name in excluded_app_list:
            debug_print('      Excluded App {0}'.format(app_name))

    else:
        # Project folder not allowed through settings.
        excluded_project_list.append(project_name)


for project_name in excluded_project_list:
    debug_print('   Excluded Project {0}'.format(project_name))


debug_print('')
