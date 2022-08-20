#!/usr/bin/env bash
###
 # Script to install required system (apt) dependencies for project on an Ubuntu Linux system.
 ##


# Set "kwarg" values for script.
key_value_args=("python_version", "ldap", "mysql")


# Import utility script.
source $(dirname $0)/../../utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


function main () {
    # Make sure we are root.
    check_user "root"

    if [[ ${!kwargs[@]} =~ "ldap" ]]
    then
        # Kwarg provided.
        ldap=${kwargs["ldap"]}
    fi
    if [[ ${!kwargs[@]} =~ "mysql" ]]
    then
        # Kwarg provided.
        mysql=${kwargs["mysql"]}
    fi

    dev_setup=""
    python_version=""

    # Check for environment flags.
    if [[ ${args[@]} =~ "dev" ]]
    then
        # Development flag provided.
        dev_setup=true

    elif [[ ${args[@]} =~ "prod" ]]
    then
        # Production flag provided.
        dev_setup=false

    else
        # Environment flags not provided. Clarify from user.
        user_confirmation "Is this a local development setup? (Alternative is a production setup)"
        dev_setup=$return_value
        echo ""
        echo ""
    fi

    # Check for python version kwarg.
    if [[ ${!kwargs[@]} =~ "python_version" ]]
    then
        # Kwarg provided.
        python_version=${kwargs["python_version"]}
    else
        # Kwarg not provided.
        # Get Python version. Should be in format of "#.#".
        valid_python=""
        while [[ ! $valid_python ]]
        do
            echo -e "Enter Python version for Project ${color_cyan}[ 3.8, 3.9, 3.10 ]${color_reset}:"
            read user_input
            if [[ $user_input = "3.8" || $user_input = "3.9" || $user_input = "3.10" ]]
            then
                echo ""
                valid_python=true
                python_version=$user_input
                echo ""
            else
                echo "Invalid input. Please enter version, such as \"3.9\" or \"3.10\"."
                echo ""
                echo ""
            fi
        done
    fi
    if [[ "$mysql" == true ]]
    then
    # remove "#" comment from #mysqlclient in requirements.txt so we can install it
        if grep -q "# mysqlclient" "../requirements.txt";
        then
            sed -i 's/# mysqlclient/mysqlclient/' "../requirements.txt"
        fi
    fi
    echo ""
    if [[ "$ldap" == true ]]
    then
    # remove "#" comment from #mysqlclient in requirements.txt so we can install it
        if grep -q "# ldap3" "../requirements.txt";
        then
            sed -i 's/# ldap3/ldap3/' "../requirements.txt"
        fi
    fi
    echo ""
    echo ""

    # Install apt-get packages.
    echo -e "${color_blue}Updating apt package list...${color_reset}"
    apt-get update > /dev/null
    apt-get install curl -y > /dev/null

    # Install Apache packages.
    echo -e "${color_blue}Installing apache dependencies...${color_reset}"
    apt-get install apache2 apache2-dev libapache2-mod-wsgi-py3 -y > /dev/null

    # Install Redis packages.
    echo -e "${color_blue}Installing redis dependencies...${color_reset}"
    apt-get install redis-server -y > /dev/null

    # Install Python packages.
    echo -e "${color_blue}Installing Python$python_version dependencies...${color_reset}"
    apt-get install python3 python3-dev python3-venv -y > /dev/null
    apt-get install "python$python_version" "python$python_version-dev" "python$python_version-venv" -y > /dev/null

    # Install Node/Npm packages.
    echo -e "${color_blue}Installing npm dependencies...${color_reset}"
    sudo ./general/installers/misc/npm_install.sh > /dev/null 2>&1

    # Install Sass packages.
    echo -e "${color_blue}Installing sass dependencies...${color_reset}"
    apt-get purge --auto-remove ruby-sass -y > /dev/null 2>&1
    npm install -g sass > /dev/null 2>&1

    # Install Printer packages.
    echo -e "${color_blue}Installing printer connection dependencies...${color_reset}"
    apt-get install libcups2-dev -y > /dev/null 2>&1
    apt-get install smbclient -y > /dev/null 2>&1

    # Install Misc packages.
    # Seems required for Ubuntu16 to install requirements.txt file when using Python3.9.
    sudo apt install libffi-dev -y > /dev/null 2>&1

    # Optionally install Mysql packages.
    if [[ "$mysql" == true ]]
    then
        echo -e "${color_blue}Installing MySQL dependencies...${color_reset}"
        apt-get install mysql-server libmysqlclient-dev -y > /dev/null
    else
        echo -e "${color_blue}Skipping MySQL dependencies...${color_reset}"
    fi

    # Optionally install Ldap packages.
    if [[ "$ldap" == true ]]
    then
        echo -e "${color_blue}Installing Ldap dependencies...${color_reset}"
        apt-get install libldap2-dev libsasl2-dev -y > /dev/null
    else
        echo -e "${color_blue}Skipping Ldap dependencies...${color_reset}"
    fi

    # Other packages, based on dev or prod environment.
    if [[ "$dev_setup" == true ]]
    then
        echo -e "${color_blue}Installing Selenium Testing dependencies...${color_reset}"
        # Google Chrome "chromium" driver for running selenium with chrome.
        if [[ ! -f "/usr/local/bin/chromedriver" ]]
        then
        # check what chrome version is installed and download chrome driver accordingly
        # unfortunately chromedriver only has generalized packages ex 97.xx.xx for all chromes with version 97
        # maybe in future this will work
#            chrome_version=$(google-chrome --product-version)
#            wget https://chromedriver.storage.googleapis.com/$chrome_version/chromedriver_linux64.zip
            wget https://chromedriver.storage.googleapis.com/97.0.4692.71/chromedriver_linux64.zip
            unzip chromedriver_linux64.zip -d /usr/local/bin/ > /dev/null
            chmod +x /usr/local/bin/chromedriver > /dev/null
            rm chromedriver_linux64.zip > /dev/null
        fi
        # Firefox "gecko" driver for running selenium with firefox.
        if [[ ! -f "/usr/local/bin/geckodriver" ]]
        then
            wget https://github.com/mozilla/geckodriver/releases/download/v0.29.1/geckodriver-v0.29.1-linux64.tar.gz
            sh -c 'tar -x geckodriver -zf geckodriver-v0.29.1-linux64.tar.gz -O > /usr/local/bin/geckodriver' > /dev/null
            chmod +x /usr/local/bin/geckodriver > /dev/null
            rm geckodriver-v0.29.1-linux64.tar.gz > /dev/null
        fi
    else
        echo -e "${color_blue}Skipping Selenium Testing dependencies...${color_reset}"

        echo -e "${color_blue}Installing Nginx dependencies...${color_reset}"
        apt-get install nginx -y > /dev/null
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


# Warn user with prompt. Skip if "force" arg was provided.
if [[ ${args[@]} =~ "force" ]]
then
    # Force command provided. Skipping prompt.
    # First remove arg as it's no longer necessary.
    args=${args[@]#force}
    main "${args[0]}"

elif [[ ${args[@]} =~ "-f" ]]
then
    # Force flag provided. Skipping prompt.
    # First remove arg as it's no longer necessary.
    args=${args[@]#-f}
    main "${args[0]}"

else
    # Display friendly prompt to user.
    echo ""
    echo "Note: This script will install system packages."
    echo -e "      ${color_cyan}To cancel, hit ctrl+c now. Otherwise hit enter to start.${color_reset}"
    read user_input
    echo ""

    main "${args[0]}"
fi

