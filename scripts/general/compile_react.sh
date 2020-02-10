#!/usr/bin/env bash
###
 # Script to compile all css files in all subprojects.
 ##


# Abort on error.
set -e


# Import utility script.
source $(dirname $0)/../utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


function main () {
    echo "Possible params:"
    echo "   * watch - Watches for changes."
    echo ""

    # Variables.
    command=""
    watch="browserify"

    # Determine command format from passed args.
    if [[ ${args[@]} =~ "watch" ]]
    then
        watch="watchify -v"
    fi

    # Determine directories to compile.
    for dir in ../*/*/*/* ../*/*/*/*/*/*
    do
        # Check if actually a directory.
        if [[ -d $dir ]]
        then
            # Check if folder name ends in "css".
            if [[ $dir == *"/js" ]]
            then
                # Check that react directory exists.
                if [[ -d $dir/react ]]
                then
                    js_dir=$dir
                    # Loop through all files in react subfolder
                    for file in $dir/react/*
                    do
                        # Check if actually a file.
                        if [[ -f $file ]]
                        then
                            # Get base file name.
                            filename=$(basename "${file%.*}")

                            # Create command.
                            new_command="npx $watch -t [ babelify --presets [env react] ] $file -o $js_dir/$filename.js"

                            # Check if previous command exists.
                            if [[ $command == "" ]]
                            then
                                # Previous command exists. Append.
                                command="$command && $new_command"
                            else
                                command="$new_command"
                            fi
                        fi
                    done
                fi
            fi
        fi
    done

    # Check that command is going to compile anything.
    if [[ $command != "" ]]
    then
        echo -e "${color_blue}Installing npm depenencies.${color_reset}"
        cd ..
        npm install
        cd ./scripts/
    fi

    # Display command to user.
    echo ""
    echo "Running command:"
    echo $command
    echo ""
    $command
    echo ""
}


main
