# Django - CAE Workspace > Documents > setup.md


## Description
Instructions for setting up this project for first time use. This documentation is mostly intended for a
local/development setup, not a server/production setup.

**NOTE**: There is a "first time setup" script accessible via `<workspace_root>/scripts/run.sh install`. This script
should automatically walk you through all the below setup, taking care of most of it for you. This documentation is
mostly provided in the event that the script errors out, or your OS of choice is not yet supported by said scripts.


## Setting Up Python
This Project runs on Python and Django. Currently, it should be able to run on any Python version 3.8 or higher.

It is strongly recommended to use a Python virtual environment for this project.

### Installing Python
#### Installing Python for Linux
Depending on your OS, you may not have the desired version of Python available.<br>
To install a specific version of Python, you will need to run:
* ```sudo apt install python3-dev python<version> python<version>-dev python<version>-venv```
    * Where <version> is the version of Python used in your environment.
    * Ex, Python3.9 would be:
        * ```sudo apt python3-dev python3.9 python3.9-dev python3.9-venv```

#### Installing Python for Windows
Currently, Windows does not ship with any version of Python.<br>
Please visit <https://www.python.org/downloads/> to download the desired version of Python.


### Setting up a Virtual Environment
It's highly recommended to create a virtual environment for this project. For details on Python Virtual Environments,
please see <https://git.ceas.wmich.edu/Python/ExampleProjects/virtual_environments>.

Once your environment is installed, load it in the terminal. Change to the project root folder and enter:
* ```pip install -r requirements.txt```

NOTE: All the dependencies under the `Production Imports` section are commented out by default. These are dependencies
which are not essential to run the project in development, but may be added if desired.

To add them, simply uncomment the desired lines and run the above command again.


## Project Setup
Once your Python Virtual Environment is set up, are a few extra steps required before the project will run properly.

### Importing Child Projects
First, change to the `apps/` folder and git clone any additional projects you wish to incorporate. Note that these
projects will have to have been whitelisted in `workspace/settings/allowed_apps.py` to run.

If you need to use any git branch other than the `master` branch, remember to change that now.

### Local env.py File
First, go to the `workspace/settings/local_env` folder. Copy `env_example.py` to project root as `env.py`, or else the
project will not run.

If desired, you can also edit this new `env.py` file as you wish, but the default values should work fine for a
standard development setting.

This file includes things like "log file directory location", "selenium testing settings", "default test password for
project accounts", and more.

NOTE: Many of these default values are not appropriate for production, and thus should be changed whenever being used
live on a server.

### Development Mode
To switch between production and development modes, the project simply checks for a file called **DEBUG** in the project
root folder. Simply create this file to run in development mode.

Development mode is useful, as it provides things like additional output on errors, so it's good for development
purposes. However, it's also technically less secure, so the project should be run in production mode whenever being
used live on a server.

### Database Setup
#### MySQL
By default, Django will use SqLite for the database. This is fine for development purposes.

However, for production, or if you prefer to use MySQL, then you will have to do the following:
* Install MySQL for your machine.
* Install the required packages in your Python environment with the `pip install mysqlclient` command.
* Create a new database in MySQL, for Django to use.
* Open up your env file (found at `workspace/settings/local_env/env.py`) and locate the `DATABASES` section.
    * Set `'ENGINE': 'django.db.backends.mysql'`
    * Change the rest of the settings as appropriate for your local setup.

#### Make Migrations
Depending on what has or has not been put onto the production server, it's possible some of the database migrations
will not have been commited yet. Thus, to be safe, always first run:
* ```python manage.py makemigrations```

#### Migrate
Next, we want to create an actual database with the migrations. To do this, run:
* ```python manage.py migrate```
NOTE: If you want the database in any format other than SQLite, make sure you change the `env.py` file accordingly,
before running this command.

#### Optionally Seed Data
At this point, if desired, we can use a custom command to seed our database. Seeding will both import preset fixtures,
and create a number of randomized records (default of 100 per applicable model).

Note that not all models have fixtures to import, and not all models will get randomized seeds. It depends on what the
model is and which makes sense to give the model. But each model should get one or the other, at the very least.

To seed data, run:
* ```python manage.py seed```
  * Optionally, you can append a number to the end to change how many random records are created per model.
    * Ex: ```python manage.py seed 10``` will only create 10 random records per model.

### Compiling CSS
At this point, the project should be able to run, but we still don't have any css to load. This is because most project
CSS comes in the form of SASS, which needs to be compiled. To compile it, we need to install `npm-sass`.

This will require first installing `npm` for your machine, then running:
* `npm install -g sass`

Once sass is installed, open a terminal and run `scripts/run.sh compile_css`. This should compile all project css files.
This includes both files in the CAE_Workspace and files in subprojects under the `apps/` folder.

### Install Redis for Websocket Handling
#### Installing Redis on Arch Linux
* ```pacman -S redis```
* ```systemctl enable redis```
* ```systemctl start redis```

#### Installing Redis on Ubuntu
* ```sudo apt-get install redis-server```

#### Installing Redis on Windows
* ???

### Optionally Install LDAP
For additional help with LDAP, consult, consult: <https://www.python-ldap.org/en/latest/installing.html>.
#### Installing LDAP on Arch Linux
* ???

#### Installing LDAP on Windows
* ```sudo apt install libldap2-dev libsasl2-dev```

#### Installing LDAP on Windows
* ???
