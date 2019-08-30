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

Otherwise, to get started, run `scripts/installers/first_time_setup.sh`.



---------

# Below is Old Information to Move at a Later Date
## Development Notes

### Front End

* Title Tag Template:
    * The title is in format of **[ Page | App | Site ]**, which seems to be the standard that Google, Stack Overflow,
    Django, and other major sites currently go by.
    * To be as generic as possible, the "Site" part of the title is set to default as "CAE Center". Where appropriate,
    this should be overridden with the website name (CAEWeb, West, etc).

* Main Nav and Subnav Menu Format:
    ```
    <li><a href="">Main Item 1</a></li>
    <li><a href="">Main Item 2</a></li>
    <li>
        <a href="">Main Item 3</a>
        <ul>
            <li><a href="">SubItem Item 1</a></li>
            <li><a href="">SubItem Item 2</a></li>
            <li><a href="">SubItem Item 3</a></li>
        </ul>
    </li>
    ```

### Back End

* User model separation:
    * The user model is split into two parts:
        * **User** - Contains fields relevant to authentication.
        * **Profile** - A one-to-one (User-correlated) model, which contains all other non-auth values.


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
