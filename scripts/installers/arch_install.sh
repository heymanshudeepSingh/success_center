#!/usr/bin/env bash
# Script to install required system (pacman) dependencies for project on a arch linux system.


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


function main() {

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

    user_confirmation "Install MySQL dependency requirements?"
    mysql=$return_value
    echo ""

    # Install packman packages.
    echo -e "${color_blue}Updating pacman package list...${color_reset}"
    pacman -Syy

    echo ""
    echo -e "${color_blue}Installing gitk dependencies...${color_reset}"
    pacman -S tk --noconfirm

    echo ""
    echo -e "${color_blue}Installing redis dependencies...${color_reset}"
    pacman -S redis --noconfirm
    systemctl enable redis
    systemctl start redis

    echo ""
    echo -e "${color_blue}Installing sass dependencies...${color_reset}"
    pacman -S ruby-sass --noconfirm
    pacman -S ruby-rb-fsevent --noconfirm

    if [[ "$mysql" = true ]]
    then
        echo ""
        echo -e "${color_blue}Installing MySQL dependencies...${color_reset}"

        # Install mysql.
        pacman -S mysql --noconfirm

        # Setup initial mysql config.
        mysql_install_db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
        systemctl enable mariadb.service
        systemctl start mariadb.service

        # Run mysql secure installation for full setup.
        mysql_secure_installation

        # Set proper permissions.
        chown mysql:root -R /var/lib/mysql
        find /var/lib/mysql -type d -exec chmod g+rwx {} \;
        chmod g+rw -R /var/lib/mysql

        # Set extra database config values.
        echo "" >> /etc/mysql/my.cnf
        echo "#" >> /etc/mysql/my.cnf
        echo "# Set default character set." >> /etc/mysql/my.cnf
        echo "#" >> /etc/mysql/my.cnf
        echo "[client]" >> /etc/mysql/my.cnf
        echo "default-character-set = utf8" >> /etc/mysql/my.cnf
        echo "" >> /etc/mysql/my.cnf
        echo "[mysqld]" >> /etc/mysql/my.cnf
        echo "collation_server = utf8_unicode_ci" >> /etc/mysql/my.cnf
        echo "character_set_server = utf8" >> /etc/mysql/my.cnf
        echo "" >> /etc/mysql/my.cnf
        echo "[mysql]" >> /etc/mysql/my.cnf
        echo "default-character-set = utf8" >> /etc/mysql/my.cnf
        echo "" >> /etc/mysql/my.cnf
        echo "" >> /etc/mysql/my.cnf
        echo "#" >> /etc/mysql/my.cnf
        echo "# Allow auto-completion in MySQL client." >> /etc/mysql/my.cnf
        echo "#" >> /etc/mysql/my.cnf
        echo "auto-rehash" >> /etc/mysql/my.cnf
        echo "" >> /etc/mysql/my.cnf

        # Restart database to read in modified setup.
        systemctl restart mariadb.service

        # Install python mysql dependencies.
        pacman -S python-mysqlclient --noconfirm
    fi

    echo ""
    echo -e "${color_blue}Installing Selenium Testing dependencies...${color_reset}"
    pacman -S python-selenium --noconfirm
    # Google Chrome "chromium" driver for running selenium with chrome.
    pacman -S chromium --noconfirm
    # Firefox "gecko" driver for running selenium with firefox.
    pacman -S geckodriver --noconfirm

    # Success. Exit script.
    echo ""
    echo -e "${color_green}Installation has finished. Terminating Arch Install script.${color_reset}"
    exit 0
}


main
