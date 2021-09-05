#!/usr/bin/env bash
###
 # Script to compile all css files in all subprojects.
 ##


# Abort on error
set -e


# Import utility script.
source $(dirname $0)/../utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


function main () {
    # Make sure we are not root.
    check_not_user "root"


    if [[ ${args[@]} =~ "hide" ]]
    then
        # Hide arg passed. Skip displaying params.
        true
    else
        # Display params.
        echo -e "${color_blue}Possible params:${color_reset}"
        echo "   * watch - Watches for changes."
        echo "   * dev - Compile in human-legible format."
        echo "   * trace - Adds backtracing to troubleshoot errors."
        echo "   * hide - Hides stdout of script."
        echo ""
        echo ""
    fi

    # Variables.
    watch="--update"
    compress="--style compressed"
    trace=""
    hide=false
    css_directories=()

    # Determine command format from passed args.
    if [[ ${args[@]} =~ "watch" ]]
    then
        watch="--watch"
    fi
    if [[ ${args[@]} =~ "dev" ]]
    then
        compress=""
    fi
    if [[ ${args[@]} =~ "trace" ]]
    then
        trace=" --trace"
    fi
    if [[ ${args[@]} =~ "hide" ]]
    then
        hide=true
    fi

    # Determine directories to compile.
    for dir in ../*/*/*/* ../*/*/*/*/*/*
    do
        # Check if actually a directory.
        if [[ -d ${dir} ]]
        then
            # Check if folder name ends in "css".
            if [[ ${dir} == *"/css" ]]
            then
                # Check if watch command was set. Annoyingly, this changes sass syntax.
                if [[ ${watch} == "--update" ]]
                then
                    # Check that sass directory exists.
                    if [[ -d ${dir}/sass ]]
                    then
                        # Loop through all files in sass subfolder.
                        for file in ${dir}/sass/*
                        do
                            # Check if actually a file.
                            if [[ -f ${file} ]]
                            then
                                # Check that file follows sass compilation file naming convention.
                                if [[ ${file} != *"/css/sass/_"*".scss" ]]
                                then
                                    # Add file to list of compile locations.
                                    filename=$(basename "${file%.*}")
                                    css_directories+=("${file}:${dir}/${filename}.css")

                                    # Remove old file before compiling, if present.
                                    rm -f "${dir}/${filename}.css" "${dir}/${filename}.css.map"
                                fi
                            fi
                        done
                    fi
                else
                    # Check that sass directory exists.
                    if [[ -d ${dir}/sass ]]
                    then
                        # Add directory to list of compile locations.
                        css_directories+=("${dir}/sass:${dir}")

                        # Loop through all files in sass subfolder.
                        for file in ${dir}/sass/*
                        do
                            # Check if actually a file.
                            if [[ -f ${file} ]]
                            then
                                # Check that file follows sass compilation file naming convention.
                                if [[ ${file} != *"/css/sass/_"*".scss" ]]
                                then
                                    filename=$(basename "${file%.*}")

                                    # Remove old file before compiling, if present.
                                    rm -f "${dir}/${filename}.css" "${dir}/${filename}.css.map"
                                fi
                            fi
                        done
                    fi
                fi
            fi
        fi
    done

    if [[ -z ${watch} ]]
    then
        watch=
    fi

    # Combine variables to create command.
    command="sass ${watch} ${css_directories[*]} ${compress} ${trace}"

    # Handle based on if "hide" arg was passed or not.
    if [[ ${hide} == true ]]
    then
        # Hide arg passed. Do not show output.
        echo -e "${color_blue}Compiling CSS files...${color_reset}"
        ${command} > /dev/null
    else
        # Display full stdout.
        echo -e "${color_blue}Running command:${color_reset}"
        echo ${command}
        ${command}
        echo ""
    fi
}


main
