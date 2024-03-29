"""
Manages and auto-installs apps for project.
"""

# User Imports.
from workspace.settings.reusable_settings import *


APP_DIR = os.path.join(BASE_DIR, 'apps')

debug_print('')


# Django base apps, any 3rd party add-on apps, and CAE_Home app.
# All other CAE Apps should be defined under the "Allowed_CAE_Apps" setting.
INSTALLED_APPS = [
    'cae_home.apps.CaeHomeConfig',
    'cae_tools.apps.CaeToolsConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'admin_reorder',
    'channels',
    'django_filters',
    'phonenumber_field',
    'rest_framework',

    'webpack_loader',
]


# List of allowed apps to automatically install.
# Formatted as a dictionary of sub-dictionary values.
# If a third party app is already installed, it will safely be ignored.
ALLOWED_CAE_PROJECTS = {
    # 'Example_Project': {
    #     'name': 'Example',
    #     'index': 'example:index',
    #     'url-prefix': 'root_url',
    #     'related_apps': {
    #         'example_project_app_1': {
    #             'config': 'apps.ExampleProjectApp1Config', # Path to Config
    #         },
    #         'example_project_app_2': {},
    #     },
    #     'third_party_apps': [
    #         'example_third_party',
    #     ],
    # },

    # "Main" project for internal CAE Center employee use.
    'CAE_Web': {
        'name': 'CAE Web',
        'index': 'cae_web_core:index',
        'url-prefix': 'caeweb',
        'related_apps': {
            'cae_web_core': {
                'config': 'apps.CaeWebCoreConfig',
            },
            'cae_web_checklists': {},
            'cae_web_scheduling': {
                'config': 'apps.CaeWebSchedulingConfig',
            },
            'cae_web_room_checkouts': {},
            'cae_web_shifts': {},
            'cae_web_work_log': {},
        },
        'third_party_apps': [],
    },

    # Communicates with and tracks logging/errors that occur in the CAEMon desktop app.
    # (Not yet created in Python as of summer 2022.
    # Exists in Laravel but Laravel version is currently unused since CAEMon switched to Python.
    # In theory, we should recreate it eventually, but it's low priority.)
    'CAEMon_Web': {
        'name': 'CAEMon Web',
        'index': '',
        'url-prefix': 'caemon',
        'related_apps': {
            'caemon_web_core': {},
        },
        'third_party_apps': [],
    },

    # Pairs with the CAEMon desktop app to track computer usage in labs.
    'CICO': {
        'name': 'Check In Check Out',
        'index': 'cico_core:index',
        'url-prefix': 'cico',
        'related_apps': {
            'cico_core': {},
        },
        'third_party_apps': [],
    },

    # For CAE Center admins to check in computers and create work tickets for students/professors.
    # Interfaces with Redmine, which then does most of the work. This just handles initial generation.
    'Drop_Off': {
        'name': 'Drop Off',
        'index': 'drop_off_core:index',
        'url-prefix': 'drop_off',
        'related_apps': {
            'drop_off_core': {
                'config': 'apps.DropOffCoreConfig',
            },
        },
        'third_party_apps': [],
    },

    # Helps the Dean's Office manage incoming graduate student applications for processing.
    'Grad_Applications': {
        'name': 'Graduate Applications',
        'index': 'grad_applications_core:index',
        'url-prefix': 'grad_apps',
        'related_apps': {
            'grad_applications_core': {},
            'grad_applications_committees': {},
            'grad_applications_processing': {},
        },
        'third_party_apps': [],
    },

    # Used by main campus to track tutoring information.
    'Success_Center': {
        'name': 'Success Center',
        'index': 'success_center_core:index',
        'url-prefix': 'success_center',
        'related_apps': {
            'success_center_core': {},
            'success_center_timesheets': {},
        },
        'third_party_apps': [],
    },
}


casefolded_project_dict = {}
# Set all project keys to be case insensitive.
for key in ALLOWED_CAE_PROJECTS.keys():
    casefolded_project_dict[str(key).casefold()] = ALLOWED_CAE_PROJECTS[key]
    casefolded_project_dict[str(key).casefold()]['official_name'] = key

ALLOWED_CAE_PROJECTS = casefolded_project_dict

# Automatically populated for automatic url generation on home page. Do not edit.
INSTALLED_CAE_PROJECTS = {}
# Automatically populated url-based dict for installed apps. Used in app main nav template generation.
INSTALLED_APP_URL_DICT = {}
# Logic to automatically install a given allowed app, if found.
installed_app_count = 1
excluded_project_list = []


# First iterate through list of all project folders within the apps folder.
debug_print('Automatically Installed Apps:')
project_folder_list = [
    x for x in os.listdir(APP_DIR) if os.path.isdir(os.path.join(APP_DIR, x)) and not x.startswith('__')
]
for project_folder_name in project_folder_list:
    # Set to ignore string casing.
    project_key_name = project_folder_name.casefold()

    # Check that project is defined through settings.
    project_defined_by_key = False
    project_defined_by_official_name = False
    if project_folder_name in ALLOWED_CAE_PROJECTS.keys():
        project_defined_by_key = True
    elif project_folder_name in [x['official_name'] for x in ALLOWED_CAE_PROJECTS.values()]:
        project_defined_by_official_name = True

    # If was defined in settings, proceed.
    if project_defined_by_key or project_defined_by_official_name:
        debug_print('   {0}Included Project{1}: {2}'.format(
            ConsoleColors.bold_blue,
            ConsoleColors.reset,
            project_folder_name,
        ))

        # Grab all app folders within given project.
        project_folder_path = os.path.join(APP_DIR, project_folder_name)
        app_folder_list = [
            str(x).casefold() for x in os.listdir(project_folder_path)
            if os.path.isdir(os.path.join(project_folder_path, x)) and
               not x.startswith('.git') and not x.startswith('_')
        ]
        included_app_list = []
        excluded_app_list = []

        # Iterate through project apps.
        for app_name in app_folder_list:

            # Check that app is defined through settings.
            try:
                # Check that app is defined through settings.
                if app_name in ALLOWED_CAE_PROJECTS[project_key_name]['related_apps']:
                    app = 'apps.{0}.{1}'.format(project_folder_name, app_name)
                    config = ALLOWED_CAE_PROJECTS[project_key_name]['related_apps'][app_name].get('config')
                    if config:
                        # Add the Config to the INSTALLED_APPS
                        # We don't override 'app' because that is used for urls later
                        new_app = 'apps.{0}.{1}.{2}'.format(project_folder_name, app_name, config)
                        INSTALLED_APPS.insert(1, new_app)
                    else:
                        INSTALLED_APPS.insert(1, app)
                    INSTALLED_CAE_PROJECTS[project_key_name] = ALLOWED_CAE_PROJECTS[project_key_name]
                    INSTALLED_CAE_PROJECTS[project_key_name]['related_apps'][app_name] = app
                    debug_print('       {0}Included App{1}: {2:<25}   {0}Url{1}: .../{3}/{2}/'.format(
                        ConsoleColors.bold_blue,
                        ConsoleColors.reset,
                        app_name,
                        INSTALLED_CAE_PROJECTS[project_key_name]['url-prefix']
                    ))
                    INSTALLED_APP_URL_DICT[INSTALLED_CAE_PROJECTS[project_key_name]['url-prefix']] = '{0}_core/app_nav.html'.format(project_key_name)
                    installed_app_count += 1
                    included_app_list.append(app_name)
                else:
                    # App not allowed through settings.
                    excluded_app_list.append(app_name)
            except KeyError:
                # No related apps key. All apps automatically excluded.
                excluded_app_list.append(app_name)

        # Print out all whitelisted but not found apps.
        delete_list = []
        for app_name in ALLOWED_CAE_PROJECTS[project_key_name]['related_apps']:
            if app_name not in included_app_list and app_name not in excluded_app_list:
                debug_print('       {0}Missing App{1}:  {2}'.format(ConsoleColors.bold_yellow, ConsoleColors.reset, app_name))
                delete_list.append(app_name)

        # Remove all references to whitelisted but not found apps.
        for item in delete_list:
            del ALLOWED_CAE_PROJECTS[project_key_name]['related_apps'][item]

        # Print out all excluded apps.
        for app_name in excluded_app_list:
            debug_print('       {0}Excluded App{1}: {2}'.format(ConsoleColors.bold_red, ConsoleColors.reset, app_name))

        # Add any third party apps.
        for third_party_app in ALLOWED_CAE_PROJECTS[project_key_name].get('third_party_apps', []):
            if third_party_app in INSTALLED_APPS:
                debug_print('       Ignoring Third Party App: {0:<14}  Already Installed.'.format(third_party_app))
                continue
            INSTALLED_APPS.insert(installed_app_count, third_party_app)
            debug_print('       {0}Included Third Party App{1}: {2}'.format(
                ConsoleColors.bold_blue,
                ConsoleColors.reset,
                third_party_app
            ))

    else:
        # Project folder not allowed through settings.
        excluded_project_list.append(project_folder_name)

# Print out excluded projects.
for project_name in excluded_project_list:
    debug_print('   {0}Excluded Project{1}: {2}'.format(ConsoleColors.bold_red, ConsoleColors.reset, project_name))


# Create list of urls, formatted in way templating can understand (For some reason, above implementations resulted
# in templates only recognizing project_name keys, but nothing further).
INSTALLED_APP_DETAILS = []
for project, project_settings in INSTALLED_CAE_PROJECTS.items():
    INSTALLED_APP_DETAILS.append(project_settings)


# Define Admin_Reorder variable for third party "admin customization" app.
ADMIN_REORDER = (
    {
        'app': 'cae_home',
        'label': 'Core User Models',
        'models': (
            'auth.Group',
            'auth.Permission',
            'cae_home.User',
            'cae_home.GroupMembership',
            'cae_home.UserIntermediary',
            'cae_home.WmuUser',

            'cae_home.Profile',
            'cae_home.Address',
            'cae_home.PhoneNumber',
            'cae_home.SiteTheme',
        ),
    },
    {
        'app': 'cae_home',
        'label': 'Core WMU Models',
        'models': (
            'cae_home.StudentHistory',
            'cae_home.Department',
            'cae_home.Major',
            'cae_home.WmuClass',
            'cae_home.RoomType',
            'cae_home.Room',
            'cae_home.Semester',
        ),
    },
    {
        'app': 'cae_home',
        'label': 'Core CAE Models',
        'models': (
            'cae_home.Asset',
            'cae_home.Software',
            'cae_home.SoftwareDetail',
        ),
    },
)

# Add installed apps into Admin_Reorder value. Logic specific to apps would go here.
for project, project_settings in INSTALLED_CAE_PROJECTS.items():
    for app, app_name in project_settings['related_apps'].items():
        formatted_name = app.replace('_', ' ').title().replace('Cae', 'CAE')
        ADMIN_REORDER += ({'app': app, 'label': formatted_name},)


debug_print('')
