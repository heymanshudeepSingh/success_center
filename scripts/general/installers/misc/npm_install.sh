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

    # Install base node/npm packages.
    curl -fsSL https://deb.nodesource.com/setup_lts.x -y > /dev/null 2>&1 | sudo -E bash -
    apt-get upgrade -y > /dev/null 2>&1
    apt-get install nodejs -y > /dev/null 2>&1
    apt-get install npm -y > /dev/null 2>&1

    # Install NodeJs "version manager".
    npm install -g n > /dev/null 2>&1

    # Verify we have the latest stable version of npm.
    n stable > /dev/null 2>&1

    # Update to latest version of npm.
    npm install -g npm@latest > /dev/null 2>&1

    # Install update checker for npm.
    npm install -g npm-check-updates > /dev/null 2>&1

    echo -e "${color_blue}NodeJs, Npm, and React dependencies installed.${color_reset}"
    echo "    NodeJs Version:  $(node -v)"
    echo "    Npm Version:     $(npm -v)"
    echo "    React Version:   $(npm view react version)"
}


main
