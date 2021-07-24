#!/usr/bin/env bash
###
 # Script to clear all automatically generated PyCache files.
 #
 # For when you get nonsensical errors about PyCache, particularly when using PyTest.
 # It seems entirely arbitrary when they pop up, and the easiest way to fix it is just to delete the associated PyCache
 # files, so the project regenerates them.
 #
 # Thus, this script simply iterates through all project folders and clears all PyCache files.
 ##


# Abort on error
set -e


# Import utility script.
source $(dirname $0)/../utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


function main () {
    cd ..

    # Get absolute path of project root.
    project_root_folder="$(cd "$(dirname "${1}")" && pwd)/$(basename "${1}")"

    echo -e "${text_blue}Starting Directory: \"${project_root_folder}\"${text_reset}"
    echo ""
    echo "Removing auto-generated files in PyCache directories:"

    # Start with current directory, which should be project root. Pass in absolute path as start point.
    iterate_dir ${project_root_folder}

    echo ""
    echo -e "${text_blue}PyCache directories cleared. Terminating script.${text_reset}"
}


###
 # Iterates through current dir, recursively checking for subdirectories and clearing any PyCache files.
 ##
function iterate_dir () {

    # Parse variables.
    dir="$(cd "$(dirname "${1}")" && pwd)/$(basename "${1}")"
    dir_name=${dir##*/}

    # Change to indicated directory.
    cd ${1}

    # Check if PyCache directory.
    if [[ "${dir_name}" == "__pycache__" ]]
    then
        # Is PyCache directory. Check all files within.
        echo "    ${dir}"
        for file in "${dir}/"*
        do
            # Check if value is actually a file.
            if [[ -f "${file}" ]]
            then
                # Is file. Double check that is PyCache file. It should end in ".pyc".
                file_extension=${file##*.}
                if [[ "${file_extension}" == "pyc" ]]
                then
                    # Is confirmed PyCache file. These are automatically generated so we can simply delete it.
                    rm ${file}
                fi
            fi
        done
    fi

    # Check for any subdirectories.
    for sub_dir in "${dir}/"*
    do
        # Check if value is actually directory.
        if [[ -d ${sub_dir} ]]
        then
            # Recursively iterate on subdirectory.
            iterate_dir ${sub_dir}
        fi
    done

    cd ..
}


main
