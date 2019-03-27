#!/usr/bin/env bash
# Script to install required apt dependencies for project on a linux system.


return_value=""


function user_confirmation () {
    # Display passed prompt and get user input.
    # Return true on "yes" or false otherwise.
    echo "$1 [ yes | no ]"
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
        echo "Please run script as sudo user. Terminating script."
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
    apt-get update

    echo ""
    echo "Installing apache dependencies."
    apt-get install apache2 apache2-dev libapache2-mod-wsgi-py3 -y

    echo ""
    echo "Installing redis dependencies."
    apt-get install redis-server -y

    echo ""
    echo "Installing Python$python_version dependencies."
    apt-get install "python$python_version" "python$python_version-dev" -y

    if [[ "$mysql" = true ]]
    then
        echo ""
        echo "Installing MySQL dependencies."
        apt-get install mysql-server libmysqlclient-dev -y
    fi

    if [[ "$ldap" = true ]]
    then
        echo ""
        echo "Installing Ldap dependencies."
        apt-get install libldap2-dev libsasl2-dev -y
    fi

    # Success. Exit script.
    echo ""
    echo "Installation has finished."
    exit 0
}

main
