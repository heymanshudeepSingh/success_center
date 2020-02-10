#!/usr/bin/env bash
###
 # Basic script to restart production server.
 ##


# Import utility script.
source $(dirname $0)/utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


function main () {
    # Make sure we are root.
    check_user "root"


    echo "Restarting Django server..."

    service nginx restart
    service uwsgi restart
    service daphne restart

    echo "Server restarted."
    echo ""
    echo "To run this manually, use the following commands:"
    echo "    sudo service nginx restart"
    echo "    sudo service uwsgi restart"
    echo "    sudo service daphne restart"
}


main
