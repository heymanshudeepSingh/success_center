#!/usr/bin/env bash
###
 # Main script to make it easier to run all subdirectory scripts.
 ##


# Import utility script.
source $(dirname $0)/utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


###
 # Script main.
 ##
function main () {
    echo "Starting \"scripts/run.sh\" script."
    echo ""

    # Check if no args were passed.
    if [[ ${#args[@]} -eq 0 && ${#kwargs[@]} -eq 0 ]]
    then
        # No values passed in. Display help menu.
        main_help
    else
        # Run selected function.
        $1
    fi
    echo ""
    echo "Terminating \"scripts/run.sh\" script."
}


###
 # Displays general helper text for main script.
 ##
function main_help() {
    echo "This script is provided for easy runtime/execution of all subscripts in the CAE Workspace project."
    echo "For more details about an option, enter the option with the \"-h\" or \"--help\" flags."
    echo ""
    echo "Available options are:"
    echo ""
    echo "General:"
    echo "    first_time_setup - Installs dependencies and sets up project for the first time on a machine."
    echo ""
    echo "Development:"
    echo "    compile_css - Compiles all SASS files to CSS."
    echo "    reset_db - Resets the local project database. Only works for SqLite."
    echo "    reset_migrations - Removes all uncommited migration files."
    echo ""
    echo "Production:"
    echo "    restart_server - Restarts all major processes for the Django project in a production environment."
    echo "    set_file_permissions - Sets all project file permissions for serving in a production environment."
    echo ""
}


###
 # Runs the script for a first time project setup.
 ##
function first_time_setup () {
    ./installers/first_time_setup.sh
}


###
 # Displays helper text for script.
 ##
function first_time_setup_help () {
    echo "Installs dependencies and sets up project for the first time on a machine."
}


###
 # Runs the script for compiling css.
 ##
function compile_css () {
    ./development/compile_css.sh
}


###
 # Displays helper text for script.
 ##
function compile_css_help () {
    echo "Compiles all SASS files to CSS."
}


###
 # Runs the script for resetting the local project database. Only works for SqLite.
 ##
function reset_db() {
    ./development/reset_db.sh
}


###
 # Displays helper text for script.
 ##
function reset_db_help () {
    echo "Resets the local project database. Only works for SqLite."
}


###
 # Runs the script for removing all uncommited migration files from CAE Workspace and all included subprojects.
 ##
function reset_migrations() {
    ./development/reset_migrations.sh
}


###
 # Displays helper text for script.
 ##
function reset_migrations_help () {
    echo "Removes all uncommited migration files."
}


###
 # Runs the script for restarting major Django processes in production environments.
 ##
function restart_server() {
    ./production/restart_server.sh
}


###
 # Displays helper text for script.
 ##
function restart_server_help () {
    echo "Restarts all major processes for the Django project in a production environment."
}


###
 # Runs the script for setting file permissions in production environments.
 ##
function set_file_permissions() {
    ./production/set_file_permissions.sh
}


###
 # Displays helper text for script.
 ##
function set_file_permissions_help () {
    echo "Sets all project file permissions for serving in a production environment."
}


main ${@}
