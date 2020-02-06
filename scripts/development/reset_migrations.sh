#!/usr/bin/env bash
###
 # Script to remove all uncommitted migrations.
 ##


# Abort on error
set -e


# Import utility script.
source $(dirname $0)/../utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


function main () {
    echo ""
    echo -e "${color_blue}Resetting migrations... ${color_reset}"


    # Loop through all CAE Workspace migrations.
    for dir in ../*/*
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
                        # Check if migration file is commited. Only remove if not.
                        if [[ $(git ls-files --error-unmatch $file 2>/dev/null) == "" ]]
                        then
                            # Finally purge selected files.
                            echo "  Removing $file"
                            rm -f $file
                        fi
                    fi
                done
            fi
        fi
    done


    # Loop through all imported subproject migrations.
    for dir in ../apps/*
    do
        # Check if actually a directory.
        if [[ -d $dir ]]
        then
            cd $dir

            # Get all directories in folder.
            for sub_dir in $(pwd)/*/*
            do
                # Check if folder name ends in "migrations".
                if [[ $sub_dir == *"migrations" ]]
                then
                    # Loop through all files in folder.
                    for file in $sub_dir/*
                    do
                        # Check if actually a file.
                        if [[ -f $file ]]
                        then
                            # Check that file follows migration name format.
                            if [[ $file == *"migrations/0"*".py" ]]
                            then
                                # Check if migration file is commited. Only remove if not.
                                if [[ $(git ls-files --error-unmatch $file 2>/dev/null) == "" ]]
                                then
                                    # Finally purge selected files.
                                    echo "  Removing $file"
                                    rm -f $file
                                fi
                            fi
                        fi
                    done

                fi
            done
            cd ../../scripts/
        fi
    done


    echo ""
    echo -e "${color_green}Migrations have been purged.${color_reset}"
    echo ""
    echo "Note that committed migrations are not touched by this script."
    echo "Only uncommitted migrations have been reset."
    echo ""
}


# Warn user with prompt. Skips if arg of "force" was provided.
if [[ ! ${args[@]} =~ "force" ]]
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
