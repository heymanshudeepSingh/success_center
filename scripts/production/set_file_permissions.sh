#!/usr/bin/env bash
# Basic script to set (reset) project file permissions.


color_reset='\033[0m'
color_red='\033[1;31m'


function main () {
    # Make sure we are root.
    if [ "$USER" != "root" ]
    then
        echo ""
        echo -e "${color_red}Please run script as sudo user. Terminating script.${color_reset}"
        echo ""
        exit 0
    else
        cd "$(dirname "$0")/../.."

        echo "Setting project file permissions..."

        find . -type d -exec chmod u+rwx {} \;  # Set all directors to be read/write/executable by user owner.
        find . -type d -exec chmod g+rwx {} \;  # Set all directories to be read/write/executable by group owners.
        find . -type d -exec chmod o-rwx {} \;    # Remove directory write/executable access by other users.
        find . -type f -exec chmod u+rw {} \;   # Set all files to be read/writeable by user owner.
        find . -type f -exec chmod g+rw {} \;   # Set all files to be read/writeable by group owners.
        find . -type f -exec chmod o-rwx {} \;    # Remove file write/executable access by other users.

        echo ""
        echo "Set all directories to be read/write/executable by user and group owners."
        echo "Set all files to be read/writable by user and group owners."
        echo "Removed all permissions for any other users."
    fi
}

main
