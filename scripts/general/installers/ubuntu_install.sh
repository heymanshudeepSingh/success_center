#!/usr/bin/env bash
###
 # Script to install required system (apt) dependencies for project on an Ubuntu Linux system.
 ##


# Import utility script.
source $(dirname $0)/../../utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


function main () {
    # Make sure we are root.
    check_user "root"


    # Display friendly prompt to user.
    echo ""
    echo "Note: This script will install system packages."
    echo -e "      ${color_cyan}To cancel, hit ctrl+c now. Otherwise hit enter to start.${color_reset}"
    read user_input


    valid_python=""
    python_version=""
    mysql=""
    ldap=""
    dev_setup=""

    user_confirmation "Is this a local development setup? (Alternative is a production setup)"
    dev_setup=$return_value
    echo ""

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
    apt-get install curl

    echo ""
    echo -e "${color_blue}Installing apache dependencies...${color_reset}"
    apt-get install apache2 apache2-dev libapache2-mod-wsgi-py3 -y

    echo ""
    echo -e "${color_blue}Installing redis dependencies...${color_reset}"
    apt-get install redis-server -y

    echo ""
    echo -e "${color_blue}Installing Python$python_version dependencies...${color_reset}"
    apt-get install python3 python3-dev python3-venv -y
    apt-get install "python$python_version" "python$python_version-dev" "python$python_version-venv" -y

    echo ""
    echo -e "${color_blue}Installing sass dependencies...${color_reset}"
    apt-get install ruby-sass -y

    echo ""
    echo -e "${color_blue}Installing npm dependencies...${color_reset}"
    curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
    apt-get install nodejs -y
    apt-get install npm -y
    sudo ./general/installers/misc/npm_install.sh

    if [[ "$mysql" = true ]]
    then
        echo ""
        echo -e "${color_blue}Installing MySQL dependencies...${color_reset}"
        apt-get install mysql-server libmysqlclient-dev -y
    else
        echo ""
        echo -e "${color_blue}Skipping MySQL dependencies...${color_reset}"
    fi

    if [[ "$ldap" = true ]]
    then
        echo ""
        echo -e "${color_blue}Installing Ldap dependencies...${color_reset}"
        apt-get install libldap2-dev libsasl2-dev -y
    else
        echo ""
        echo -e "${color_blue}Skipping Ldap dependencies...${color_reset}"
    fi

    if [[ "$dev_setup" = true ]]
    then
        echo ""
        echo -e "${color_blue}Installing Selenium Testing dependencies...${color_reset}"
        # Google Chrome "chromium" driver for running selenium with chrome.
        if [[ ! -f "/usr/local/bin/chromedriver" ]]
        then
            wget https://chromedriver.storage.googleapis.com/2.46/chromedriver_linux64.zip
            unzip chromedriver_linux64.zip -d /usr/local/bin/
            chmod +x /usr/local/bin/chromedriver
            rm chromedriver_linux64.zip
        fi
        # Firefox "gecko" driver for running selenium with firefox.
        if [[ ! -f "/usr/local/bin/geckodriver" ]]
        then
            wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
            sh -c 'tar -x geckodriver -zf geckodriver-v0.24.0-linux64.tar.gz -O > /usr/local/bin/geckodriver'
            chmod +x /usr/local/bin/geckodriver
            rm geckodriver-v0.24.0-linux64.tar.gz
        fi
    else
        echo ""
        echo -e "${color_blue}Skipping Selenium Testing dependencies...${color_reset}"

        echo ""
        echo -e "${color_blue}Installing Nginx dependencies...${color_reset}"
        apt-get install nginx -y
        systemctl disable nginx
        systemctl stop nginx
        echo -e "${color_blue}Nginx server installed.${color_reset}"
        echo -e "${color_blue}Note: If you got errors on installation, then nginx probably installed but had a conflict with apache.${color_reset}"
        echo -e "${color_blue}      Only one program (apache or nginx) can watch port 80 at a time.${color_reset}"
        echo -e "${color_blue}      Try disabling apache and then restarting nginx.${color_reset}"
        echo ""
        echo -e "${color_blue}To enable Nginx on computer start, run \"sudo systemctl enable nginx\".${color_reset}"
        echo -e "${color_blue}To start Nginx now, run \"sudo systemctl start nginx\".${color_reset}"
    fi

    # Success. Exit script.
    echo ""
    echo -e "${color_green}Installation has finished. Terminating Ubuntu Install script.${color_reset}"
    exit 0
}

main
