# Django - CAE Workspace > Documents > readme.md

## Description
This folder contains the main documentation for the project. If nothing else, make sure to read this document before
starting work on the project.

## Other Documentation
For information on getting started with this project, see `setup.md`.

For information on how project CSS structure is setup, see `css.md`.

For information on using React or Javascript, see `javascript_and_react.md`.

For information on middleware, see `middleware.md`.

For information on using datetime recurrence rules, see `datetime_recurrence_rules.md`.

For information on production deployment, see `deployment.md`.

## Workspace > SubProject > SubApp Structure
### CAE Workspace
This project (`cae_workspace`) essentially just acts as a core/housing for all other CAE Center Django projects.
Essentially, in an attempt to reduce code redundancy, all "universal logic" is contained in this workspace. That
includes main page templating, core css layouts, models which are used in two or more projects, etc.

As result, by itself, this `cae_workspace` project does very little. However, by using it as a base to import other
projects, it ensures that all models/front end/etc is universal between all of those projects, thus (in theory) reducing
overall work required and cost of maintaining future sites at the CAE Center.

### SubProject Import Structure
The `apps` folder found at the project root is empty, by default. However, putting other Django projects there (such as
through `git clone`) will dynamically import that project logic. Thus, putting multiple Django projects within the
`apps` folder will turn them into one, larger, cohesive site, so to speak.

These SubProjects all follow standard Django conventions, and thus logic should be split into apps, when appropriate.
The logic in `cae_workspace` will automatically handle and import appropriately, as long as whitelisted accordingly in
the `settings/allowed_apps.py` file.

### Adding a New Project/App
Logic is already in place to automatically import SubProjects and associated Apps. However, for security reasons, they
first must be whitelisted appropriately before they will import.

To add a new Project/App:
* First clone the desired SubProject into the `apps` folder. For the most part, follow standard Django practices for
creating this SubProject and all related Apps.
    * The only exception is that each SubProject should have an App called `<project_name>_core`. This is what
    `cae_workspace` searches for to hook into and dynamically import logic.
        * For example, with a SubProject of `CAE_Web`, it would need a App called `cae_web_core` for it to import
        properly.
    * Because this "core" App is required, note that this is also a good location for the SubProject to contain logic
    that hooks into the workspace, for example, to use the "universal" css/templating/etc.
* Open up `settings/allowed_apps.py`.
* Scroll down to `ALLOWED_CAE_APPS` and follow the example provided.
* Once the new SubProject or App is added, it should automatically be imported from that point on, as long as it is
present inside the `apps` folder.

