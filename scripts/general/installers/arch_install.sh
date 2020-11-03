#!/usr/bin/env bash
###
 # Script to install required system (pacman) dependencies for project on a Arch Linux system.
 # Note that script assumes arch linux will be a development environment.
 ##


# Import utility script.
source $(dirname $0)/../../utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


function main() {
    # Make sure we are root.
    check_user "root"


    # Display friendly prompt to user.
    echo ""
    echo "Note: This script will install system packages."
    echo -e "      ${color_cyan}To cancel, hit ctrl+c now. Otherwise hit enter to start.${color_reset}"
    read user_input

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
    echo -e "${color_blue}Installing npm dependencies...${color_reset}"
    pacman -S nodejs npm --noconfirm
    sudo ./general/installers/misc/npm_install.sh

    echo ""
    echo -e "${color_blue}Installing sass dependencies...${color_reset}"
    npm install -g sass

    echo ""
    echo -e "${color_blue}Installing sass dependencies...${color_reset}"
    pacman -S libcups --noconfirm
    pacman -S smbclient --noconfirm

    if [[ "$mysql" = true ]]
    then
        echo ""
        echo -e "${color_blue}Installing MySQL dependencies...${color_reset}"

        # Call MariaDB Arch install script.
        sudo ./general/installers/misc/arch_maria_db_install.sh
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
