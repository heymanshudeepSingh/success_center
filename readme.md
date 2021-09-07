# Django - CAE Workspace

## Environment Versions
This project should be compatible with all versions of Python 3.6 or higher.

Production environment is expected to be an Ubuntu server. But testing/development has also been done on Arch Linux,
Ubuntu Desktop, and Windows. If you use any other OS types, or see anything missing/incorrect in this documentation,
please update it accordingly.

## Description

A Django "workspace" to function as the core for future CAE Center projects.

Intended to be as general as possible. Most views/templates and specific page logic should go into separate SubProjects
and SubApps, to be located in the **apps** folder.

For more information, see the `documentation/readme.md` file.

Otherwise, to get started, run `scripts/general/installers/first_time_setup.sh`.


## Tests
Run tests with `python manage.py test`.

To skip Selenium (browser page tests, which can run slow/take a while), use the command
`python manage.py test --exclude-tag=functional`.

---------

# Below is Old Information to Move at a Later Date

## Deployment and Hosting

To deploy, you will likely want to do the following on your host/server:

### Establishing Production Settings in Settings.py

* Make sure to set the appropriate database info.
* Update static media urls.
* Set the proper "Allowed Host" addresses.
* Set security settings:
    * **TODO**: List security settings.
* You can doublecheck validity of these settings with **manage.py check --deploy**.

### Setting Up Apache

* Check if Apache is currently installed:
    * **dpkg --get-selections | grep apache**
* Install Apache (For Ubuntu Systems):
    * **sudo apt install apache2 apache2-dev libapache2-mod-wsgi-py3**
* Install wsgi packages on desired Python environment:
    * **pip install mod_wsgi**
* Set either project owner or group permissions to Apache's:
    * **sudo chown www-data ./myProjectRootDirectory**
        * OR
    * **sudo chown :www-data ./myProjectRootDirectory**
* Configure Apache settings:
    * TODO: List apache settings. https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-apache-and-mod_wsgi-on-ubuntu-14-04 is currently good reference.
* Reload Apache:
    * **sudo service apache2 reload**
