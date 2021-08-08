#!/usr/bin/env bash
###
 # Script to compile all JavaScript files in all subprojects.
 #
 # For JavaScript, that means:
 #  * Actively compiling any React files (this is required for them to run in a web browser).
 #  * Combining all our various JavaScript files into a single file, for production serving.
 #
 # Note that complicated array syntax is acquired from https://github.com/koalaman/shellcheck/wiki/SC2089
 # Was required in order to make the code execute without errors.
 ##


# Abort on error.
set -e


# Import utility script.
source $(dirname $0)/../utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


###
 # Program entrypoint.
 ##
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
        echo "   * hide - Hides stdout of script."
        echo ""
        echo ""
    fi

    compile_command=""
    merge_command=""

    # Determine directories to compile.
    for dir in ../*/*/*/* ../*/*/*/*/*/*
    do
        # Check if actually a directory.
        if [[ -d ${dir} ]]
        then
            # Check if folder name ends in "js".
            if [[ ${dir} == *"/js" ]]
            then
                # Clear folders of any previously compiled JavaScript code.
                clear_dist_folder

                # Get compile command.
                compile_react
                if [[ ${compile_command} == "" ]]
                then
                    # Does not exist. Create.
                    compile_command=("${return_value}")
                else
                    # Previous command exists. Append.
                    compile_command+=(" ${return_value}")
                fi

                # Get merge command.
                merge_js
                # Check if previous command exists.
                if [[ ${merge_command} == "" ]]
                then
                    # Does not exist. Create.
                    merge_command=("${return_value}")
                else
                    # Previous command exists. Append.
                    merge_command+=(" ${return_value}")
                fi
            fi
        fi
    done

    # Now run commands, determined above.
    # Check that commands are going to execute anything.
    if [[ ${compile_command[@]} != "" || ${merge_command[@]} != "" ]]
    then
        echo ""
        echo -e "${color_blue}Installing npm dependencies.${color_reset}"
        cd ..
        if [[ ${args[@]} =~ "hide" ]]
        then
            # Hide arg passed.
            npm install > /dev/null
        else
            npm install
        fi
        cd ./scripts/

        # Execute depending on provided "watch" arg.
        if [[ ${args[@]} =~ "watch" ]]
        then
            # Watch provided by user.
            full_command=(npx concurrently "${compile_command[@]}" "${merge_command[@]}")

            echo ""
            echo -e "${color_blue}Compiling React and Merging JavaScript:${color_reset}"
            echo "${full_command[@]}"
            echo ""
            "${full_command[@]}"
            echo ""

        else
            # Watch not provided by user.
            compile_command=(npx concurrently "${compile_command[@]}")

            # Handle based on if "hide" arg was passed or not.
            if [[ ${args[@]} =~ "hide" ]]
            then
                # Hide arg passed.
                echo -e "${color_blue}Compiling React Code.${color_reset}"
                "${compile_command[@]}"  > /dev/null
            else
                # Display full stdout.
                echo ""
                echo -e "${color_blue}Compiling React Code:${color_reset}"
                echo "${compile_command[@]}"
                "${compile_command[@]}"
                echo ""
            fi

            merge_command=(npx concurrently "${merge_command[@]}")

            # Handle based on if "hide" command was passed or not.
            if [[ ${args[@]} =~ "hide" ]]
            then
                # Hide arg passed.
                echo -e "${color_blue}Merging JavaScript Files.${color_reset}"
                "${merge_command[@]}" > /dev/null
            else
                # Display full stdout.
                echo ""
                echo -e "${color_blue}Merging JavaScript Files:${color_reset}"
                echo "${merge_command[@]}"
                echo ""
                "${merge_command[@]}"
                echo ""
            fi
        fi
    fi

    echo -e "${color_blue}Compile JS script complete.${color_reset}"
}


###
 # Function to clear all files out of the "js/dist/" folder, if it exists yet.
 #
 # In order for below functions to behave as expected, it's easier to simply clear out this folder before running either
 # one. This ensure that "old, previously compiled code" is never accidentally included in new compile attempts, such
 # as due to logic errors or similar.
 #
 # Easiest way to do this is just to naively remove and recreate the "js/dist/" folder.
 ##
function clear_dist_folder() {
    # Check that react directory exists.
    if [[ -d ${dir}/dist ]]
    then
        # Compiled/temporary directory "dist" exists. Remove.
        rm -r ${dir}/dist

        # Recreate directory.
        mkdir ${dir}/dist
    fi
}


###
 # Function to compile all React files into proper JavaScript.
 # Required in order for React code to run in a web browser.
 #
 # This function should be run when console is located within a JavaScript static file directory, such as
 # "<project_app>/static/<app_name>/js/".
 #
 # From this directory, this function will search for a "js/react/" folder. It is assumed that all project React files
 # will always be in this type of folder setup, if React files exist for the given app.
 #
 # If said folder exists, then this attempts to compile react folders to "js/dist/".
 ##
function compile_react() {
    # Variables.
    command=""
    watch="browserify"

    # Determine command format from passed args.
    if [[ ${args[@]} =~ "watch" ]]
    then
        watch="watchify -v"
    fi

    # Check that react directory exists.
    if [[ -d ${dir}/react ]]
    then
        js_dir=${dir}
        # Loop through all files in react subfolder
        for file in ${dir}/react/*
        do
            # Check if actually a file.
            if [[ -f ${file} ]]
            then
                dir_basename=${dir%/*}
                dir_basename=${dir_basename##*/}
                if [[ ${args[@]} =~ "hide" ]]
                then
                    # Hide arg passed. Skip displaying output.
                    true
                else
                    echo -e "${color_blue}${dir_basename}: Found React files to compile.${color_reset}"
                fi

                # Get base file name.
                filename=$(basename "${file%.*}")

                # Create directory.
                if [[ ! -d ${dir}/dist ]]
                then
                    mkdir ${dir}/dist
                fi

                # Create command.
                if [[ ${command} == "" ]]
                then
                    # Does not exist. Create.
                    command=("npx ${watch} -t [ babelify --presets [@babel/preset-env @babel/preset-react] ] ${file} -o ${js_dir}/dist/${filename}.js")
                else
                    # Previous command exists. Append.
                    command+=(" npx ${watch} -t [ babelify --presets [@babel/preset-env @babel/preset-react] ] ${file} -o ${js_dir}/dist/${filename}.js")
                fi
            fi
        done
    fi

    return_value=${command[@]}
}


###
 # Function to merge smaller JavaScript files into one single, larger file.
 # For production, it's cleaner if we only serve a single file for each app.
 #
 # This function should be run when console is located within a JavaScript static file directory, such as
 # "<project_app>/static/<app_name>/js/".
 #
 # From this directory, this function searches for all JavaScript files located either at this base "js/" folder, or any
 # found within "js/dist/".
 #
 # For any JavaScript files found, this function attempts to merge them into a single file at "js/dist/", which has the
 # name automatically generated from the project app, aka "<app_name>.js".
 #
 # So for example, if this is run in the "cae_home" JavaScript static files folder, then it will create a single large
 # JavaScript file at "js/dist/cae_home.js" which is meant to be served in production.
 ##
function merge_js() {
    # Variables.
    command=""
    watch="browserify"

    # Determine command format from passed args.
    if [[ ${args[@]} =~ "watch" ]]
    then
        watch="watchify -v"
    fi

    # Check if folder name ends in "js".
    if [[ "${dir}" == *"/js" && "${dir}" != *"third_party/js" ]]
    then
        # Merge JS files in directory.
        file_set=""
        dir_basename=${dir%/*}
        dir_basename=${dir_basename##*/}
        if [[ ${args[@]} =~ "hide" ]]
        then
            # Hide arg passed. Skip displaying output.
            true
        else
            echo -e "${color_blue}${dir_basename}: Found JS files to merge.${color_reset}"
        fi

        # Add all files in react directory.
        # Annoyingly, we have to check these separately to prevent occassional nonsensical compile errors.
        for file in ${dir}/react/*
        do
            # Check that item is a file.
            if [[ -f ${file} ]]
            then
                # Append file to file_set string.
                if [[ ${file_set} == "" ]]
                then
                    # Handle empty string.
                    file_set="${file}"
                else
                    # Append to existing fileset.
                    file_set+=" ${file}"
                fi
            fi
        done

        # Add all files in directory. Ignore files in subfolders.
        for file in ${dir}/*
        do
            # Check that item is a file.
            if [[ -f ${file} ]]
            then
                # Get file path info.
                file_name=${file##*/}
                file_dir=${file%/*}
                file_path=${file_dir}/react/${file_name}

                # Check if react version of file exists.
                if [[ -d ${dir}/react && -f ${file_path} ]]
                then
                    # React version exists. Already added so we can safely ignore file.
                    file=""
                fi

                # Check that file should be added.
                if [[ ${file} != "" ]]
                then
                    # Append file to file_set string.
                    if [[ ${file_set} == "" ]]
                    then
                        # Handle empty string.
                        file_set="${file}"
                    else
                        # Append to existing fileset.
                        file_set+=" ${file}"
                    fi
                fi
            fi
        done

        # Check that files were found to compile.
        if [[ ${file_set} != "" ]]
        then
            # Create directory.
            if [[ ! -d ${dir}/dist ]]
            then
                mkdir ${dir}/dist
            fi

            # Create command.
            new_command="npx ${watch} -t [ babelify --presets [@babel/preset-env @babel/preset-react] ] ${file_set} -o ${dir}/dist/${dir_basename}.js"

            if [[ ${command} == "" ]]
            then
                command=("${new_command}")
            else
                command+=(" ${new_command}")
            fi
        fi
    fi

    return_value=${command[@]}
}


main
