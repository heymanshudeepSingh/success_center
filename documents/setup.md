# Django - CAE Workspace > Documents > setup.md

## Description
Instructions for setting up this project for first time use. This documentation is mostly intended for a
local/development setup, not a server/production setup.

If desired, there is a "first_time_setup" script under the `scripts/installers/` folder. This script will automatically
walk you through all the below setup, taking care of most of it for you.

## Setting Up Python
This Project runs on Python and Django. it should be able to run on any Python version 3.6 or higher.

### Installing Python
#### Installing Python for Ubuntu 16.04 or Earlier
If using Ubuntu 16.04 or earlier, you will not have a new enough version of Python to run the project.<br>
To get a newer version of Python, you will need to run:
* ```sudo apt install python<version>-dev```
    * Where <version> is the version of Python used in your environment.
    * Ex, Python3.6 would be:
        * ```sudo apt install python3.6-dev```

#### Installing Python for Windows
Currently, Windows does not ship with any version of Python.<br>
Please visit <https://www.python.org/downloads/> to download the desired version of Python.

### Setting up a Virtual Environment
It's highly recommended to create a virtual environment for this project. For details on Python Virtual Environments,
please see <https://git.ceas.wmich.edu/Python/ExampleProjects/VirtualEnvironments>.

Once your environment is installed, load it in the terminal. Change to the project root folder and enter:
* ```pip install -r requirements.txt```

NOTE: All the dependencies under the `Production Imports` section are commented out by default. These are dependencies
which are not essential to run the project in development, but may be added if desired.

To add them, simply uncomment the desired lines and run the above command again.

## Project Setup
Once your Python Virtual Environment is set up, are a few extra steps required before the project will run properly.

### Importing Child Projects
First, change to the `apps/` folder and git clone any additional projects you wish to incorporate. Note that these
projects will have to have been whitelisted in `settings/allowed_apps.py` to run.

If you need to use any git branch other than the `master` branch, remember to change that now, as well.

### Local env.py File
First, go to the `settings/local_env` folder. Copy `env_example.py` as `env.py`, or else the project will not run.

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

### Setup Database
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
** Optionally, you can append a number to the end to change how many random records are created per model.
*** Ex: ```python manage.py seed 10``` will only create 10 random records per model.

### Compiling CSS
At this point, the project should be able to run, but we still don't have any css to load. To compile it, we need to
install `ruby-sass`, as it's the only sass version that allows use of the "watch" command (at least as of writing this).

Once ruby-sass is installed (see below), simply open a terminal and run `scripts/compile_css.sh`. This should compile
all sass files into css. This includes both files in the CAE_Workspace and files in subprojects under the `apps/`
folder.

#### Installing Ruby-SASS on Arch Linux
Run the commands:
* ```pacman -S ruby-sass```
* ```pacman -S ruby-rb-fsevent```

#### Installing Ruby-SASS on Ubuntu
Run the command:
* ```apt-get install ruby-sass```

#### Installing Ruby-SASS on Windows
First, you'll need to download ruby from <https://rubyinstaller.org/downloads/>.

Once that completes, open a new terminal and run:
* ```gem install sass```
