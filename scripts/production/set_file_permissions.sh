#!/usr/bin/env bash
###
 # Basic script to set (reset) project file permissions.
 ##


# Abort on error.
set -e


# Import utility script.
source $(dirname $0)/utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


function main () {
    # Make sure we are root.
    check_user "root"


    # Default to project root, which is 1 directories up from scripts folder.
    directory_location="$(dirname "$0")/.."
    force_progress=""

    # Handle args.
    for arg in $args
    do
        # Handle if "force_progress" arg was passed.
        if [[ $arg == "force_progress" || $arg == "-f" ]]
        then
            force_progress=True

        # Handle everything else. Assume is directory location.
        elif [[ -d $arg ]]
        then
            directory_location=$arg
        fi
    done

    # Change directory.
    cd $directory_location

    # Display location and give user chance to cancel.
    echo ""
    echo -e "${color_blue}Setting permissions for directory and all sub-folders/sub-files:${color_reset}"
    echo "$(pwd)"
    echo ""
    if [[ ! $force_progress ]]
    then
        echo -e "${color_cyan}Press enter to continue or ctrl+c to cancel.${color_reset}"
        read user_input
    fi

    echo "Setting project file ownership..."
    chown www-data:ceas_programmers -R ./

    echo "Setting project file permissions..."
    find . -type d -exec chmod u+rwx {} \;  # Set all directors to be read/write/executable by user owner.
    find . -type d -exec chmod g+rwx {} \;  # Set all directories to be read/write/executable by group owners.
    find . -type d -exec chmod o-rwx {} \;  # Remove directory write/executable access by other users.
    find . -type f -exec chmod u+rw {} \;   # Set all files to be read/writeable by user owner.
    find . -type f -exec chmod g+rw {} \;   # Set all files to be read/writeable by group owners.
    find . -type f -exec chmod o-rwx {} \;  # Remove file write/executable access by other users.

    echo ""
    echo "Set all directories to be read/write/executable by user and group owners."
    echo "Set all files to be read/writable by user and group owners."
    echo "Removed all permissions for any other users."
}


main
