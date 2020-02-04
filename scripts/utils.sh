#!/usr/bin/env bash
# Utility script to provide helper functions/logic to other scripts.

echo "Starting utility script."


# Global Variables.
return_value=""
color_reset='\033[0m'
color_red='\033[1;31m'
color_green='\033[1;32m'
color_blue='\033[1;34m'
color_cyan='\033[1;36m'


###
 # Change to location of script's directory to the same directory script resides in..
 # Can help make logic more consistent, if location of terminal matters.
 ##
function normalize_directory () {
    cd "$(dirname "$0")"
}


###
 # Change location of script's directory to the project's top level "scripts" folder.
 # Can help make logic more consistent, if location of terminal matters.
 ##
function change_to_script_directory () {
    # First normalize directory, so it doesn't matter where we called from in terminal..
    normalize_directory

    # Recursively cd upwards until we find the "scripts" directory.
    # If "scripts" directory doesn't exist, then cd until we find the root directory.
    while [[ "${PWD##*/}" != "scripts" ]]
    do
        # Check if we found the root directory.
        if [[ "$(pwd)" == "/" ]]
        then
            echo ""
            echo -e "${color_red}Could not find \"scripts\" directory. Terminating script.${color_reset}"
            echo ""
            exit 0
        fi
        cd ..
    done
}


###
 #
 ##
function check_user () {
    # Check that user value was provided by first arg.
    if [[ "$1" == "" ]]
    then
        echo ""
        echo -e "${color_red}No user passed in to \"check_user\" function. Terminating script.${color_reset}"
        echo ""
        exit 0
    fi

    # Check that users match.
    if [[ "$USER" != "$1" ]]
    then
        echo ""
        echo -e "${color_red}Please run script as \"$1\" user. Terminating script.${color_reset}"
        echo ""
        exit 0
    fi
}


###
 # Display passed prompt and get user input.
 # If provided, first arg is used as output text.
 # Return true on "yes" or false otherwise.
 ##
function user_confirmation () {

    echo -e "$1 ${color_cyan}[ Yes | No ]${color_reset}"
    read user_input

    if [[ "$user_input" = "yes" ]] || [[ "$user_input" = "y" ]] || [[ "$user_input" = "YES" ]] || [[ "$user_input" = "Y" ]]
    then
        return_value=true
    else
        return_value=false
    fi
}


echo "Terminating utility script."
