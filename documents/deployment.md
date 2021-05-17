# Django - CAE Workspace > Documents > Deployment.md


## Description
Information for deploying the project on a production server.

This documentation assumes the server is running some version of Ubuntu.

For additional help, most steps for production setup are incredibly similar to steps documented in `setup.md`. Consult
that file for some additional help.
> Keep in mind that `setup.md` is more meant for a development setup, so there will be slight discrepancies.

## Django Setup Instructions

### Cloning and First Time Installation
First, clone the project down to the desired folder. Put it somewhere where you intend the project to stay, ideally
not in a local user folder.
> Subfolders within `/srv` or `/opt` may be good choices.

Note that you may need sudo permissions to set up initial project permissions.

If multiple user accounts are meant to access the project, then consider making a custom group for these users, and set
the project group permissions accordingly.

Once cloned, run `<project_root>/scripts/run.sh install`. This will guide you through initial project setup. Decline
`development environment` options whenever offered.

### Setting Up a Python Environment
The First Time Setup script should have installed all the requirements to setup a Python Virtual Environment.

For production, you'll probably want the environment in a folder outside of the project's folders.
> Once again, subfolders within `/srv` or `/opt` may be good choices.

Once at the desired location, run the command `python<version> -m venv django` where **version** is the desired version
of Python to run. Then load this environment with `source ./django/bin/activate`.

Change back to project root. Uncomment out all production libraries in `requrements.txt`, if any are commented. Finally,
run `pip install -r requirements.txt` to install all project requirements.

### Project Setup
The project is cloned, First Time Setup script has ran, and a custom Python Environment has been created and loaded.

Next, copy `<project_root>/settings/local_env/env_example.py` to `<project_root>/settings/local_env/env.py`. Edit
`env.py` and set all applicable values.

If using LDAP, also run `git submodule update --init --recursive` to pull the custom SimpleLDAP library as well.

Finally, change to the project root directory and run the following:
* `sudo ./scripts/run.sh set_permissions`
* `python manage.py collectstatic`
* `python manage.py migrate`
* `python manage.py loadfixtures`

### Security Settings
These are the latest values for these Django settings as of version 3.0.

For the most up to date info, see <https://docs.djangoproject.com/en/dev/ref/settings/>

* SECURE_SSL_REDIRECT (Default: False)
    * Indicates if Django should attempt to redirect all non-HTTPS requests to HTTPS.
    * Note that if you have something like Apache or Nginx already doing this, then this isn't necessary.
* SECURE_SSL_HOST (Default: None)
    * If a string, then indicates the url all SSL redirects will go to, when **SECURE_SSL_REDIRECT** is True.
* CSRF_COOKIE_SECURE (Default False)
    * Indicates if form cookies should only serve under HTTPS connections.
SESSION_COOKIE_SECURE (Default: False)
    * Indicates if session cookies should only serve under HTTPS connections.

* SECURE_HSTS_SECONDS (Default: False)
    * Forces browsers to refuse insecure connections to the site for a given period of time.
    * However, if configured incorrectly, can break all access to the site. See
    <https://docs.djangoproject.com/en/dev/ref/middleware/#http-strict-transport-security> for more info.
* SECURE_HSTS_INCLUDE_SUBDOMAINS (Default: False)
    * Indicates if subdomains should be considered when **SECURE_HSTS_SECONDS** is non-zero.
* SECURE_CONTENT_TYPE_NOSNIFF (Default: True)
    * Forces browsers to exclusively serve files as specified by the **Content-Type** section of the header.
* X_FRAME_OPTIONS (Default: 'Deny')
    * Set to DENY to prevent X-Frames and potential clickjacking.
* SECURE_BROWSER_XSS_FILTER (Default: False)
    * Adds X-XXS-Protection to headers for all responses that don't already have it.
    * Adds little benefit for modern browsers, but can be good to set for older browsers.

## Uwsgi, Nginx, and Daphne Setup Instructions
Once the base Django project is setup, we can then configure our server to serve the site.


