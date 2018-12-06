# Django - CAE Workspace > Settings

## Description
All the standard Django website settings go here, plus a bit of extra logic.

Main logic to note is the **allowed_apps.py** file.

Includes:
* **settings.py** - The initial, standard settings that comes with a Django project. Includes base things like middleware
definitions, template locations, and user authentication settings.
* **extra_settings.py** - A few custom values that are directly related to settings.py. Includes logging definition, secret
key generation, and handling of launching dev/production environments.
* **allowed_apps.py** - Loaded at the start of settings.py. This controls the "dynamic importing" of sub projects and
related apps. If it's not explicitly defined in this file, then it won't be imported.
* **reusable_settings.py** - Not technically settings, per say, but helper values that are directly used within above
settings values. Includes things like debug print (for before logging is properly initialized) and color print output.
* **local_env** folder - Contains project logging files, as well as any settings which are likely to change per
individual machine.
* **urls.py** - The standard "site-wide" url importing that comes with any Django project. Has a bit of extra logic due
to site's "dynamic importing" functionality.
* **routing.py** - Django Channel's equivalent to urls.py. Used for socket connections.
