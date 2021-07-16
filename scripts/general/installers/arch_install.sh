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

    # Install pacman packages.
    echo -e "${color_blue}Updating pacman package list...${color_reset}"
    pacman -Syy > /dev/null

    echo -e "${color_blue}Installing gitk dependencies...${color_reset}"
    pacman -S tk --needed --noconfirm> /dev/null

    cho -e "${color_blue}Installing pytest dependencies...${color_reset}"
    pacman -S python-pytest --needed --noconfirm> /dev/null

    echo -e "${color_blue}Installing redis dependencies...${color_reset}"
    pacman -S redis --needed --noconfirm > /dev/null
    systemctl enable redis > /dev/null
    systemctl start redis > /dev/null

    echo -e "${color_blue}Installing npm dependencies...${color_reset}"
    pacman -S nodejs npm --needed --noconfirm > /dev/null 2>&1
    sudo ./general/installers/misc/npm_install.sh > /dev/null 2>&1

    echo -e "${color_blue}Installing sass dependencies...${color_reset}"
    npm install -g sass > /dev/null

    echo -e "${color_blue}Installing printer connection dependencies...${color_reset}"
    pacman -S libcups --needed --noconfirm > /dev/null
    pacman -S smbclient --needed --noconfirm > /dev/null

    if [[ "$mysql" = true ]]
    then
        echo -e "${color_blue}Installing MySQL dependencies...${color_reset}"

        # Call MariaDB Arch install script.
        sudo ./general/installers/misc/arch_maria_db_install.sh > /dev/null
    fi

    echo -e "${color_blue}Installing Selenium Testing dependencies...${color_reset}"
    pacman -S python-selenium --needed --noconfirm > /dev/null
    # Google Chrome "chromium" driver for running selenium with chrome.
    pacman -S chromium --needed --noconfirm > /dev/null
    # Firefox "gecko" driver for running selenium with firefox.
    pacman -S geckodriver --needed --noconfirm > /dev/null

    # Success. Exit script.
    echo ""
    echo -e "${color_green}Installation has finished. Terminating Arch Install script.${color_reset}"
    exit 0
}


main
