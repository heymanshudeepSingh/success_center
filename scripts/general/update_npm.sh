#!/usr/bin/env bash
###
 # Script to update all npm dependencies.
 ##


# Abort on error
set -e


# Import utility script.
source $(dirname $0)/../utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


function main () {
    # Make sure we are not root.
    check_not_user "root"


    # Remove node_modules directory to start from scratch.
    if [[ -d ../node_modules/ ]]
    then
        cd ..
        rm -r ./node_modules
        cd ./scripts/
    fi

    # Update npm dependency versions.
    echo -e "${color_blue}Automatically updating npm package dependencies to newest versions.${color_reset}"
    ncu -u

    # Install npm dependencies.
    echo ""
    echo ""
    echo -e "${color_blue}Installing npm dependencies.${color_reset}"
    npm install

    # echo ""
    # echo ""
    # echo -e "${color_blue}Attempting to update remaining dependencies.${color_reset}"
    # npm install -g npm-check-updates

    # Attempt to fix audit issues.
    echo ""
    echo ""
    echo -e "${color_blue}Attempting to correct dependency vulnerabilities.${color_reset}"
    npm audit fix

    echo ""
    echo -e "${color_green}Npm dependencies updated.${color_reset}"
    echo -e "${color_green}Remember to test changes by attempting to compile react.${color_reset}"
    echo -e "${color_green}If anything fails, attempt to troubleshoot or revert version of issue dependencies before commiting.${color_reset}"
}


main
