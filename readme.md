# Django - CAE Workspace


## Environment Versions
This project should be compatible with all versions of Python 3.8 or higher.

Production environment is expected to be an Ubuntu server. But testing/development has also been done on Arch Linux,
Ubuntu Desktop, and Windows (although Windows hasn't been tested in a while). If you use any other OS types, or see
anything missing/incorrect in this documentation, please update it accordingly.


## Description
A Django "workspace" to function as the core for future CAE Center projects.

Intended to be as general as possible. Most views/templates and specific page logic should go into separate SubProjects
and SubApps, to be located in the **apps** folder.

For more information, see the `documentation/readme.md` file.

Otherwise, to get started, run `scripts/run.sh install`.<br>
This installation script should take care of all initial setup, at least enough to initially run the project.


## Tests
Run tests with `python manage.py test`.

To skip Selenium (browser page tests, which can run slow/take a while), use the command
`python manage.py test --exclude-tag=functional`.


## Deployment and Hosting
Various additional documentation can be viewed by running the project and accessing the internal "DevDocs" views. This
internal documentation is only accessible when running the project in development mode.
