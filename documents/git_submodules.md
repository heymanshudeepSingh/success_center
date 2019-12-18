# Django - CAE Workspace > Documents > Git Submodules.md


## Git Submodules
This project should be used as a "git submodule". Git submodules are essentially projects that are meant to be used
within other projects.

### Installing Submodules
Submodules can be imported into another project with the command:
* ``git submodule add <project_url> <location_to_store_submodule>``<br><br>
Where:
    * `<project_url>` is the same as if you were to run `git clone` to pull the project.
    * `<location_to_store_submodule>` is the location you wish the submodule to store within the parent project.

### Initializing Submodules
When you clone a repo that uses submodules, you'll need to initialize the submodules before they can be accessed. This
can be done in one of two ways:
* Add the `--recursive` tag when you clone the parent project. This will also get all submodules (assuming they're
defined within the master branch).<br><br>
Ex: `git clone --recursive <project_url>`<br>

* If the original project was already cloned, or if the submodule wasn't in the master branch, use:<br><br>
`git submodule update --init --recursive`

### Updating Submodules
Any projects that use a submodule will automatically track which commit is being used. When a submodule is updated, the
projects using them will have to update which commit they point to.<br><br>
This is accomplished with 2 steps:
* ``git submodule foreach git pull origin master``
* Verify the pulled submodule changes are what you want, and commit them.
