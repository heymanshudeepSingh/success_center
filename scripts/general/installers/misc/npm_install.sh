#!/usr/bin/env bash
###
 # Script to install latest version of npm on local machine.
 # Note that some version of npm needs to already be installed for this to work.
 ##


# Abort on error.
set -e


# Import utility script.
source $(dirname $0)/../../../utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


function main () {
    # Make sure we are root.
    check_user "root"

    # Update to latest version of npm.
    npm install npm@latest -g

    # Install update checker for npm.
    npm install -g npm-check-updates
}


main
