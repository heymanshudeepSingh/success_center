#!/usr/bin/env bash
###
 # Script to compile all css files in all subprojects.
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


function main () {
    # Make sure we are not root.
    check_not_user "root"


    echo "Possible params:"
    echo "   * watch - Watches for changes."
    echo ""

    compile_react
    merge_js
}


function compile_react() {
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
            # Check if folder name ends in "js".
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
                            new_command="npx ${watch} -t [ babelify --presets [@babel/preset-env @babel/preset-react] ] ${file} -o ${js_dir}/${filename}.js"

                            # Check if previous command exists.
                            if [[ $command == "" ]]
                            then
                                # Does not exist. Create.
                                command=(npx concurrently "$new_command")
                            else
                                # Previous command exists. Append.
                                command+=(" $new_command")
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
    echo -e "${color_blue}Compiling React:${color_reset}"
    echo "${command[@]}"
    echo ""
    "${command[@]}"
    echo ""
}


function merge_js() {
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
            # Check if folder name ends in "js".
            if [[ $dir == *"/js" && $dir != *"third_party/js" ]]
            then
                # Merge JS files in directory.
                file_set=""
                dir_basename=${dir%/*}
                dir_basename=${dir_basename##*/}
                echo -e "${color_blue}Merging JS Files in ${dir_basename} directory.${color_reset}"

                # Add all files in directory. Ignore files in subfolders.
                for file in $dir/*
                do
                    # Check that item is a file.
                    if [[ -f $file ]]
                    then
                        if [[ $file_set == "" ]]
                        then
                            # Handle empty string.
                            file_set="${file}"
                        else
                            # Append to existing fileset.
                            file_set+=" ${file}"
                        fi
                    fi
                done

                # Check that files were found to compile.
                if [[ $file_set != "" ]]
                then
                    # Create directory.
                    if [[ ! -d ${dir}/dist ]]
                    then
                        mkdir ${dir}/dist
                    fi

                    # Create command.
                    new_command="npx ${watch} -t [ babelify --presets [@babel/preset-env @babel/preset-react] ] ${file_set} -o ${dir}/dist/${dir_basename}.js"
                    command=(npx concurrently "$new_command")


                    # Display and run command.
                    echo $(pwd)
                    echo ""
                    echo -e "${color_blue}Merging JS:${color_reset}"
                    echo "${command[@]}"
                    echo ""
                    "${command[@]}"
                    echo ""
                fi
            fi
        fi
    done

}


main
