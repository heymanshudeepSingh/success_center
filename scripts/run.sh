#!/usr/bin/env bash
###
 # Main script to make it easier to run all subdirectory scripts.
 ##


# Import utility script.
key_value_args=()
source $(dirname $0)/utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


###
 # Script main.
 ##
function main () {

    # Check if no args were passed.
    if [[ ${#args[@]} -eq 0 && ${#kwargs[@]} -eq 0 ]]
    then
        # No values passed in. Display help menu.
        main_help
    else
        check_for_help_flags

        if [[ $help_flag == true ]]
        then
            # Help flag set. Display helper text for function.
            "${args[0]}"_help
        else
            # Help flag not set. Run selected function.
            ${args[0]} "${@#${args[0]}}"
        fi
    fi
    echo ""
}


###
 # Displays general helper text for main script.
 ##
function main_help() {
    echo -e "${color_blue}run.sh${color_reset}"
    echo "    This script is provided for easy runtime/execution of all subscripts in the CAE Workspace project."
    echo "    For more details about an option, enter the option with the \"-h\" or \"--help\" flags."
    echo ""
    echo "Available options are:"
    echo ""
    echo -e "${color_blue}General${color_reset}:"
    echo "    first_time_setup - Installs dependencies and sets up project for the first time on a machine."
    echo "    compile_css - Compiles all SASS files to CSS."
    echo "    compile_react - Compiles all React files to JS."
    echo "    update_npm - Attempts to update all npm dependencies."
    echo ""
    echo -e "${color_blue}Development${color_reset}:"
    echo "    reset_db - Resets the local project database. Only works for SqLite."
    echo "    reset_migrations - Removes all uncommited migration files."
    echo ""
    echo -e "${color_blue}Production${color_reset}:"
    echo "    restart_server - Restarts all major processes for the Django project in a production environment."
    echo "    set_file_permissions - Sets all project file permissions for serving in a production environment."
}


###
 # Runs the script for a first time project setup.
 ##
function first_time_setup () {
    ./general/installers/first_time_setup.sh "${@}"
}
###
 # Aliases for "first_time_setup".
 ##
function install () {
    first_time_setup
}
function first_time_install () {
    first_time_setup
}
function setup () {
    first_time_setup
}


###
 # Displays helper text for script.
 ##
function first_time_setup_help () {
    echo -e "${color_blue}Script${color_reset}: first_time_setup.sh"
    echo "    Installs dependencies and sets up project for the first time on a machine."
    echo ""
    echo -e "${color_blue}Permissions:${color_reset} Run as non root/admin user (will ask for credentials though)."
    echo ""
    echo -e "${color_blue}Currently supports:${color_reset}"
    echo "    * Arch Linux"
    echo "    * Ubuntu Linux"
    echo "    * Windows"
    echo ""
    echo -e "${color_blue}Aliases${color_reset}:"
    echo "    * install"
    echo "    * first_time_install"
    echo "    * setup"
}
###
 # Aliases for "first_time_setup_help".
 ##
function install_help () {
    first_time_setup_help
}
function first_time_install_help () {
    first_time_setup_help
}
function setup_help () {
    first_time_setup_help
}


###
 # Runs the script for compiling css.
 ##
function compile_css () {
    ./general/compile_css.sh "${@}"
}
###
 # Aliases for "compile_css".
 ##
function css () {
    compile_css
}
function compile_sass () {
    compile_css
}
function sass () {
    compile_css
}


###
 # Displays helper text for script.
 ##
function compile_css_help () {
    echo -e "${color_blue}Script${color_reset}: compile_css.sh"
    echo "    Compiles all project SASS files to CSS."
    echo "    Includes both CAE Workspace and includes supbrojects in the \"apps\" directory."
    echo ""
    echo "    To be found, SASS files should be located in the \"<app_name>/static/<app_name>/css/sass/\" folder."
    echo "    Located files will be compiled to the \"<app_name>/static/<app_name>/css/\" folder."
    echo ""
    echo -e "${color_blue}Permissions${color_reset}: Run as non root/admin user."
    echo ""
    echo -e "${color_blue}Params${color_reset}:"
    echo "    * watch - Watches for changes."
    echo "    * dev - Compile in human-legible format."
    echo "    * trace - Adds backtracing to troubleshoot errors."
    echo ""
    echo -e "${color_blue}Aliases${color_reset}:"
    echo "    * css"
    echo "    * sass"
    echo "    * compile_sass"
}
###
 # Aliases for "compile_css_help".
 ##
function css_help () {
    compile_css_help
}
function compile_sass_help () {
    compile_css_help
}
function sass_help () {
    compile_css_help
}


###
 # Runs the script for compiling react.
 ##
function compile_react () {
    ./general/compile_react.sh "${@}"
}
###
 # Aliases for "compile_react".
 ##
function react () {
    compile_react
}
function js () {
    compile_react
}
function compile_js () {
    compile_react
}
function javascript () {
    compile_react
}
function compile_javascript () {
    compile_react
}


###
 # Displays helper text for script.
 ##
function compile_react_help () {
    echo -e "${color_blue}Script${color_reset}: compile_react.sh"
    echo "    Compiles all project React files to JS."
    echo "    Includes both CAE Workspace and includes supbrojects in the \"apps\" directory."
    echo ""
    echo "    To be found, React files should be located in the \"<app_name>/static/<app_name>/js/react/\" folder."
    echo "    Located files will be compiled to the \"<app_name>/static/<app_name>/js/\" folder."
    echo ""
    echo -e "${color_blue}Permissions${color_reset}: Run as non root/admin user."
    echo ""
    echo -e "${color_blue}Params${color_reset}:"
    echo "    * watch - Watches for changes."
    echo ""
    echo -e "${color_blue}Aliases${color_reset}:"
    echo "    * react"
    echo "    * js"
    echo "    * compile_js"
    echo "    * javascript"
    echo "    * compile_javascript"
}
###
 # Aliases for "compile_react_help".
 ##
function react_help () {
    compile_react_help
}
function js_help () {
    compile_react_help
}
function compile_js_help () {
    compile_react_help
}
function javascript_help () {
    compile_react_help
}
function compile_javascript_help () {
    compile_react_help
}


###
 # Runs the script for updating npm.
 ##
function update_npm () {
    ./general/update_npm.sh "${@}"
}
###
 # Aliases for "update_npm".
 ##
function npm () {
    update_npm
}
function npm_update () {
    update_npm
}


###
 # Displays helper text for script.
 ##
function update_npm_help () {
    echo -e "${color_blue}Script${color_reset}: update_npm.sh"
    echo "    Attempts to update all npm dependencies."
    echo ""
    echo -e "${color_blue}Permissions${color_reset}: Run as non root/admin user."
    echo ""
    echo -e "${color_blue}Aliases${color_reset}:"
    echo "    * npm"
    echo "    * npm_update"
}
###
 # Aliases for "update_npm_help".
 ##
function npm_help () {
    update_npm_help
}
function npm_update_help () {
    update_npm_help
}


###
 # Runs the script for resetting the local project database. Only works for SqLite.
 ##
function reset_db () {
    ./development/reset_db.sh "${@}"
}
###
 # Aliases for "reset_db".
 ##
function reset_database () {
    reset_db
}
function db_reset () {
    reset_db
}
function database_reset () {
    reset_db
}


###
 # Displays helper text for script.
 ##
function reset_db_help () {
    echo -e "${color_blue}Script${color_reset}: reset_db.sh"
    echo "    Resets the local project database. Currently only works for SqLite."
    echo ""
    echo -e "${color_blue}Params${color_reset}:"
    echo "    * force - Forces script to skip user confirmation promps."
    echo ""
    echo -e "${color_blue}Aliases${color_reset}:"
    echo "    * reset_database"
    echo "    * db_reset"
    echo "    * database_reset"
}
###
 # Aliases for "reset_db_help".
 ##
function reset_database_help () {
    reset_db_help
}
function db_reset_help () {
    reset_db_help
}
function database_reset_help () {
    reset_db_help
}


###
 # Runs the script for removing all uncommited migration files from CAE Workspace and all included subprojects.
 ##
function reset_migrations() {
    ./development/reset_migrations.sh "${@}"
}
###
 # Aliases for "reset_migrations".
 ##
function migrations_reset () {
    reset_migrations
}


###
 # Displays helper text for script.
 ##
function reset_migrations_help () {
    echo -e "${color_blue}Script${color_reset}: reset_migrations.sh"
    echo "    Removes all uncommited migration files."
    echo ""
    echo -e "${color_blue}Params${color_reset}:"
    echo "    * force - Forces script to skip user confirmation promps."
    echo "    * model_count - Number of models to create when seeding. Default is 100."
    echo ""
    echo -e "${color_blue}Aliases${color_reset}:"
    echo "    * migrations_reset"
}
###
 # Aliases for "reset_migrations_help".
 ##
function migrations_reset_help () {
    reset_migrations_help
}


###
 # Runs the script for restarting major Django processes in production environments.
 ##
function restart_server() {
    ./production/restart_server.sh "${@}"
}
###
 # Aliases for "restart_server".
 ##
function server_restart () {
    restart_server
}


###
 # Displays helper text for script.
 ##
function restart_server_help () {
    echo -e "${color_blue}Script${color_reset}: restart_server.sh"
    echo "    Restarts all major processes for the Django project in a production environment."
    echo ""
    echo -e "${color_blue}Permissions${color_reset}: Run as root/admin user."
    echo ""
    echo -e "${color_blue}Aliases${color_reset}:"
    echo "    * server_restart"
}
###
 # Aliases for "restart_server_help".
 ##
function server_restart_help () {
    restart_server_help
}



###
 # Runs the script for setting file permissions in production environments.
 ##
function set_file_permissions () {
    ./production/set_file_permissions.sh "${@}"
}
###
 # Aliases for "set_file_permissions".
 ##
 function set_permissions () {
    set_file_permissions
 }


###
 # Displays helper text for script.
 ##
function set_file_permissions_help () {
    echo -e "${color_blue}Script${color_reset}: set_file_permissions.sh"
    echo "    Sets all project file permissions for serving in a production environment."
    echo ""
    echo -e "${color_blue}Permissions${color_reset}: Run as root/admin user."
    echo ""
    echo -e "${color_blue}Aliases${color_reset}:"
    echo "    * set_permissions"
}
###
 # Aliases for "set_file_permissions_help".
 ##
 function set_permissions_help () {
    set_file_permissions_help
 }


main ${@}
