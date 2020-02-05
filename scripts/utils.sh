#!/usr/bin/env bash
###
 # Utility script to provide helper functions/logic to other scripts.
 #
 # Color Notes:
 #      Use colors by adding the "-e" flag to echo, otherwise it will just print out the ascii values of the color.
 #
 #      Reset - Should be used at the end of every echo that uses a color.
 #      Red - For errors.
 #      Green - For critical success?
 #      Blue - Headers to visually differentiate new sections of data to the user.
 #      Cyan - For prompts that ask the user to input a value.
 #
 # return_value:
 #      Used as a variable to save return values of functions.
 #      Necessary or else we can only return integers. Also, any integer other than 0 will count as an "error flag" and
 #          cause the scripts to terminate if the "set -e" flag is set.
 ##


# Global Variables.
return_value=""
color_reset='\033[0m'
color_red='\033[1;31m'
color_green='\033[1;32m'
color_blue='\033[1;34m'
color_cyan='\033[1;36m'
orig_args=${@}
args=()
declare -A kwargs


###
 # Processes all passed script args/kwargs.
 #
 # https://opensource.com/article/18/5/you-dont-know-bash-intro-bash-arrays
 # https://stackoverflow.com/a/3467959
 ##
function proccess_args () {
    key=""
    for arg in $orig_args
    do
        # Check if we already have a key.
        if [[ $key != "" ]]
        then

            # We have a key. Check that we don't have two in a row.
            if [[ $arg == "--"* ]]
            then
                # Found a second key immediately after the first.
                echo ""
                echo -e "${color_red}Two keys were passed in a row. Expected key, value pairs. Terminating script.${color_reset}"
                echo ""
                exit 0
            fi

            # Save key value pair.
            kwargs[$key]=$arg

            # Reset key.
            key=""
        else
            # We do not have a key.
            # Check if value is kwarg key or standard arg.
            if [[ $arg == "--"* ]]
            then
                # Check if arg is "--help". This is an exception and has no key/value relation.
                if [[ $arg == "--help" ]]
                then
                    # Handle for --help arg.
                    args+=("-h")
                else
                    # Handle for kwarg key. Save minus the "--" part.
                    key=${arg##*-}
                fi
            else
                # Handle for normal arg.
                args+=($arg)
            fi
        fi
    done
    orig_args=""

    # Check if we have a remaining key without an associated value.
    if [[ $key != "" ]]
    then
        # Found remaining key.
        echo ""
        echo -e "${color_red}Found kwarg key without passed value. Terminating script.${color_reset}"
        echo ""
        exit 0
    fi
}


###
 # Prints all args and kwargs to console.
 #
 # Array (args):
 #      Access all args with "${args[@]}"
 # Dict (kwargs):
 #      Access all keys with "${!kwargs[@]}".
 #      Access all values with "${kwargs[@]}".
 ##
function display_args () {
    echo -e "${color_blue}Displaying all passed script args and kwargs.${color_reset}"

    # Check if args are present.
    echo ""
    if [[ ${#args[@]} -eq 0 ]]
    then
        echo "No args passed to script."
    else
        # One or more values exist. Display all.

        echo "Args:"
        for arg in ${args[@]}
        do
            echo "   $arg"
        done
    fi

    # Check if kwargs are present.
    echo ""
    if [[ ${#kwargs[@]} -eq 0 ]]
    then
        echo "No kwargs passed to script."
    else
        # One or more values exist. Display all.

        echo "Kwargs:"
        for key in ${!kwargs[@]}
        do
            echo "    $key: ${kwargs[$key]}"
        done
    fi

    echo ""
}


###
 # Change to location of script's directory to the same directory script resides in..
 # Can help make logic more consistent, if location of terminal matters.
 ##
function normalize_directory () {
    cd "$(dirname "$0")"
}


###
 # Change location of script's directory to the project's top level "scripts" folder.
 # Can help make logic more consistent, if location of terminal matters.
 ##
function change_to_scripts_directory () {
    # First normalize directory, so it doesn't matter where we called from in terminal..
    normalize_directory

    # Recursively cd upwards until we find the "scripts" directory.
    # If "scripts" directory doesn't exist, then cd until we find the root directory.
    while [[ "${PWD##*/}" != "scripts" ]]
    do
        # Check if we found the root directory.
        if [[ "$(pwd)" == "/" ]]
        then
            echo ""
            echo -e "${color_red}Could not find \"scripts\" directory. Terminating script.${color_reset}"
            echo ""
            exit 0
        fi
        cd ..
    done
}


###
 # Checks if user matches provided argument.
 ##
function check_user () {
    # Check that user value was provided by first arg.
    if [[ "$1" == "" ]]
    then
        echo ""
        echo -e "${color_red}No user passed in to \"check_user\" function. Terminating script.${color_reset}"
        echo ""
        exit 0
    fi

    # Check that users match.
    if [[ "$USER" != "$1" ]]
    then
        echo ""
        echo -e "${color_red}Please run script as \"$1\" user. Terminating script.${color_reset}"
        echo ""
        exit 0
    fi
}


###
 # Display passed prompt and get user input.
 # If provided, first arg is used as output text.
 # Return true on "yes" or false otherwise.
 ##
function user_confirmation () {

    echo -e "$1 ${color_cyan}[ Yes | No ]${color_reset}"
    read user_input

    if [[ "$user_input" = "yes" ]] || [[ "$user_input" = "y" ]] || [[ "$user_input" = "YES" ]] || [[ "$user_input" = "Y" ]]
    then
        return_value=true
    else
        return_value=false
    fi
}


# Process all args.
proccess_args