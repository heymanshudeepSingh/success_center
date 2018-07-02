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
ALLOWED_CAE_PROJECTS = {
    # 'Example_Project': {
    #     'url-prefix': 'root_url',
    #     'site': {
    #         'index': 'example:index',
    #         'name': 'Example',
    #     },
    #     'related_apps': {
    #         'example_project_app_1': {},
    #         'example_project_app_2': {},
    #     }
    # },

    'CAE_Web': {
        'url-prefix': 'caeweb',
        'site': {
            'index': 'cae_web_core:index',
            'name': 'CAE Web',
        },
        'related_apps': {
            'cae_web_core': {},
            'cae_web_audio_visual': {},
        },
    },

}


# Automatically populated for automatic url generation on home page. Do not edit.
INSTALLED_CAE_PROJECTS = {}

# Logic to automatically install a given allowed app, if found.
# First iterate through list of all project folders within the apps folder.
debug_print('Automatically Installed Apps:')
project_folder_list = [
    x for x in os.listdir(APP_DIR) if os.path.isdir(os.path.join(APP_DIR, x)) and not x.startswith('__')
]
excluded_project_list = []
for project_name in project_folder_list:

    # Check that project is defined through settings.
    if project_name in ALLOWED_CAE_PROJECTS.keys():
        debug_print('   Included Project {0}'.format(project_name))

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
            try:
                if app_name in ALLOWED_CAE_PROJECTS[project_name]['related_apps']:
                    app = 'apps.{0}.{1}'.format(project_name, app_name)
                    INSTALLED_APPS.insert(0, app)
                    INSTALLED_CAE_PROJECTS[project_name] = ALLOWED_CAE_PROJECTS[project_name]
                    INSTALLED_CAE_PROJECTS[project_name]['related_apps'][app_name] = app
                    debug_print('      Included App {0}'.format(app_name))
                else:
                    # App not allowed through settings.
                    excluded_app_list.append(app_name)
            except KeyError:
                # No related apps key. All apps automatically excluded.
                excluded_app_list.append(app_name)

        for app_name in excluded_app_list:
            debug_print('{0}      Excluded App {1}{2}'.format(ConsoleColors.bold_red, app_name, ConsoleColors.reset))

    else:
        # Project folder not allowed through settings.
        excluded_project_list.append(project_name)


for project_name in excluded_project_list:
    debug_print('{0}   Excluded Project {1}{2}'.format(ConsoleColors.bold_red, project_name, ConsoleColors.reset))


debug_print('')
