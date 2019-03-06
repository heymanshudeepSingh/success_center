#!/usr/bin/env bash
# Script to compile all css files in all subprojects.


# Abort on error
set -e


# Change to location of script's directory.
# Otherwise logic is inconsistent, based on where terminal initially is.
cd "$(dirname "$0")"


# Global Variables.
args=()


###
 # Get passed script args. Seems this can't be done in a function.
 # Note that parameters are normally passed as $1, $2, $3...
 # To dynamically read all of them, some logic is needed
 ##
# Get first parameters by using a counter as part of the arg name.
counter=1
parameter="$(eval echo "\$$counter")"

# While arg is not empty.
while [[ ! -z $parameter ]]
do
    # Save arg to parameter array.
    args+=($parameter)

    # Increment counter and use it to update arg name.
    counter=$((counter+1))
    parameter="$(eval echo "\$$counter")"
done


function main () {
    echo "Possible params:"
    echo "   * watch - Watches for changes."
    echo "   * dev - Compile in human-legible format."
    echo ""

    # Variables.
    watch="--update"
    compress="--style compressed"
    css_directories=()

    # Determine command format from passed args.
    for arg in ${args[*]}
    do
        if [[ $arg == "watch" ]]
        then
            watch="--watch"
        elif [[ $arg == "dev" ]]
        then
            compress=""
        fi
    done

    # Determine directories to compile.
    for dir in ../*/*/*/* ../*/*/*/*/*/*
    do
        # Check if actually a directory.
        if [[ -d $dir ]]
        then
            # Check if folder name ends in "css".
            if [[ $dir == *"/css" ]]
            then
                # Check if watch command was set. Annoyingly, this changes sass syntax.
                if [[ $watch == "--update" ]]
                then
                    # Loop through all files in sass subfolder.
                    for file in $dir/sass/*
                    do
                        # Check that file follows sass compilation file naming convention.
                        if [[ $file != *"/css/sass/_"*".scss" ]]
                        then
                            # Add file to list of compile locations.
                            filename=$(basename "${file%.*}")
                            css_directories+=("$file:$dir/$filename.css")

                            # Remove old file before compiling, if present.
                            rm -f "$dir/$filename.css"
                        fi
                    done
                else
                    # Add directory to list of compile locations.
                    css_directories+=("$dir/sass:$dir")

                    # Remove old files before compiling.
                    for file in $dir/*
                    do
                        # Double check that value is not a directory.
                        if [[ ! -d $file ]]
                        then
                            rm -f $file
                        fi
                    done
                fi
            fi
        fi
    done

    if [[ -z $watch ]]
    then
        watch=
    fi

    # Combine variables to create command.
    command="sass $watch ${css_directories[*]} $compress"

    echo ""
    echo "Running command:"
    echo $command
    echo ""
    $command
    echo ""
}


main
