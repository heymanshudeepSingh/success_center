#!/usr/bin/env bash
# Script to remove all migrations.


# Abort on error
set -e


color_reset='\033[0m'
color_green='\033[1;32m'
color_blue='\033[1;34m'


# Change to location of script's directory.
# Otherwise logic is inconsistent, based on where terminal initially is.
cd "$(dirname "$0")"


function main () {
    echo ""
    echo -e "${color_blue}Resetting migrations... ${color_reset}"

    # Loop through all directories in 2nd and 4th levels.
    for dir in ../*/* ../*/*/*/*
    do
        # Check if actually a directory.
        if [[ -d $dir ]];
        then
            # Check if folder name ends in "migrations".
            if [[ $dir == *"migrations" ]]
            then
                echo "  Checking directory $dir"
                # Loop through all files in folder.
                for file in $dir/*
                do
                    # Check that file follows migration name format.
                    if [[ $file == *"migrations/0"*".py" ]]
                    then
                        # Finally purge selected files.
                        echo "  Removing $file"
                        rm -f $file
                    fi
                done
            fi
        fi
    done


    echo ""
    echo -e "${color_green}Migrations have been purged.${color_reset}"
    echo ""
    echo "For all projects that have committed migrations, you can get them back with a 'git reset --hard'."
    echo "However, note that this command will also reset any uncommitted code."
    echo "Be sure to commit first if you have anything you wish to preserve."
    echo ""
}


# Warn user with prompt. Skips if arg of "force" was provided.
if [[ $1 != "force" ]]
then
    echo ""
    echo "Note: This will remove all migrations in CAE_Workspace, including ones in the apps subfolders."
    echo "      This script probably shouldn't be run in production environments."
    echo "      Only proceed if you know what you are doing."
    echo "      To cancel, hit ctrl+c now. Otherwise hit enter to start."
    read userInput
    echo ""
fi


main
