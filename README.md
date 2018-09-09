# Django - CAE Home App

## Description

A Django "workspace" to function as the core for future CAE Center projects.

Intended to be as general as possible.

## Initial Set Up

* On first time use, you may want to go into **settings/local_env** and modify **env.py**.
    * **Development** - Can probably leave file as is, if using SQLite. Otherwise, edit env file as desired.
    * **Production** - Default env definitely isn't production ready. Will require modificaitons for stability and
    security.
* Make sure to run migrations to set up initial database schema.
* If developing on a local machine, create a new file called "DEBUG" in the project's root folder. Otherwise, project
will yell about "Allowed Hosts".

## React Notes

Unfortunately, React seems to prefer a syntax that browsers do not fully understand, out of the gate. To correct for
this, you will need to install "npm", and then use "browserify" to compile the code into a browser-friendly format.

(It's actually similar to how sass files compile into standard css. You write code that's easier to handle and far more
human-friendly. Then you use the console to run a compiler, changing the code into a format the browser understands.)

### Installing NPM

Npm is "the world's largest software registry" and what most front end libraries now seem to install through.

Npm now installs as part of NodeJS. The simplest way to install is to visit:
* https://nodejs.org/

### Install Required Packages

Npm will install the required development packages specified in ```packages.json```. This also handles installing the versions of each
package without conflicts.

From the project's root directory, run:
* ```npm install```

* To run local npm binaries you should add the following to your ```~/.bashrc```:

```bash
# From user hkly at https://dev.to/hkly/running-local-npm-executables-cle
# Run a local npm binary with 'npm-run COMMAND'
npm-run() {
    $(npm bin)/$*
}
```

* Reopen a terminal or run ```source ~/.bashrc``` to reload it.

### Compiling React Files through Browserify

From the project's root directory, run:
* ```npm-run browserify -t [ babelify --presets [env react] ] <sourceFile> -o <destinationFile>```
    * Where ```\<sourceFile>``` is the original react file.
    * And ```\<destinationFile>``` is where the browser-friendly file is compiled to.

### Compiling React Files through Browserify Automatically

Watchify can detect changes to source files and automatically run browserfiy
for you. You can pass the same arguments that you would use for browserify.

From the project's root directory, run:
* ```npm-run watchify -v -t [ babelify --presets [env react] ] <sourceFile> -o <destinationFile>```
    * Where ```<sourceFile>``` is the original react file.
    * And ```<destinationFile>``` is where the browser-friendly file is compiled to.
    * The ```-v``` will notify you each time a change is detected.

### Live Updates through Web Sockets

In order to have live updates, you need to run ```redis``` which handles
messaging for ```django-channels```.

* Run ```sudo apt-get install redis```

## Adding a New Project/App

This project essentially just acts as a core/workspace to house all other CAE Center Django projects.

To make usage easier, a system has been implemented to automatically import recognized sub-projects and apps. To add a
new one:
* Open up **settings/allowed_apps.py**.
* Scroll down to **ALLOWED_CAE_APPS** and follow the example provided.
* Once a new sub-project or app is added, it will automatically be imported from then on out.
    * Note: Settings will only search for sub-projects and apps inside the **apps** folder.

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

### Using MySQL

* Install required packages on machine:
    * **sudo apt-get install python3-dev libmysqlclient-dev mysql-server**
* Install required packages on desired Python environment:
    * **pip install mysqlclient**
* Create the proper database inside MySQL

### Establishing Production Settings in Settings.py

* Make sure to set the appropriate database info.
* Update static media urls.
* Set the proper "Allowed Host" addresses.
* Set security settings:
    * TODO: List security settings.
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
