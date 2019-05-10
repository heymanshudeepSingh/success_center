#!/usr/bin/env bash
# Basic script to restart production server.


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
        echo "Restarting Django server..."

        service nginx restart
        service uwsgi restart
        service daphne restart

        echo ""
        echo "To run this manually, use the following commands:"
        echo "    sudo service nginx restart"
        echo "    sudo service uwsgi restart"
        echo "    sudo service daphne restart"
    fi
}

main
