#!/usr/bin/env bash
# Script to install required apt dependencies for project on a linux system.


return_value=""
color_reset='\033[0m'
color_red='\033[1;31m'
color_green='\033[1;32m'
color_blue='\033[1;34m'
color_cyan='\033[1;36m'


###
 # Display passed prompt and get user input.
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


function main () {
    # Make sure we are root.
    if [ "$USER" != "root" ]
    then
        echo ""
        echo -e "${color_red}Please run script as sudo user. Terminating script.${color_reset}"
        echo ""
        exit 0
    else
        echo ""
        echo "Note: This script will install system packages."
        echo "      To cancel, hit ctrl+c now. Otherwise hit enter to start."
        read user_input
    fi

    valid_python=""
    python_version=""
    mysql=""
    ldap=""

    # Get Python version. Should be in format of "#.#".
    while [[ ! $valid_python ]]
    do
        echo "Enter Python version for Project (Must be Python 3.6 or higher):"
        read user_input
        if [[ $user_input = "3.6" ]] || [[ $user_input = "3.7" ]] || [[ $user_input = "3.8" ]]
        then
            echo ""
            valid_python=true
            python_version=$user_input
        else
            echo "Invalid input. Please enter version, such as \"3.6\" or \"3.7\"."
            echo ""
        fi
    done

    user_confirmation "Install MySQL dependency requirements?"
    mysql=$return_value
    echo ""

    user_confirmation "Install Ldap dependency requirements?"
    ldap=$return_value
    echo ""

    # Install apt-get packages.
    echo -e "${color_blue}Updating apt package list...${color_reset}"
    apt-get update

    echo ""
    echo -e "${color_blue}Installing apache dependencies...${color_reset}"
    apt-get install apache2 apache2-dev libapache2-mod-wsgi-py3 -y

    echo ""
    echo -e "${color_blue}Installing redis dependencies...${color_reset}"
    apt-get install redis-server -y

    echo ""
    echo -e "${color_blue}Installing Python$python_version dependencies...${color_reset}"
    apt-get install "python$python_version" "python$python_version-dev" -y

    if [[ "$mysql" = true ]]
    then
        echo ""
        echo -e "${color_blue}Installing MySQL dependencies...${color_reset}"
        apt-get install mysql-server libmysqlclient-dev -y
    fi

    if [[ "$ldap" = true ]]
    then
        echo ""
        echo -e "${color_blue}Installing Ldap dependencies...${color_reset}"
        apt-get install libldap2-dev libsasl2-dev -y
    fi

    echo ""
    echo -e "${color_blue}Installing Chromium drivers (Required for selenium testing)...${color_reset}"
    apt-get install chromium-chromedriver -y

    # Success. Exit script.
    echo ""
    echo -e "${color_green}Installation has finished. Terminating script.${color_reset}"
    exit 0
}

main
