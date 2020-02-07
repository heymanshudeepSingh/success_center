#!/usr/bin/env bash
###
 # Utility script to provide helper functions/logic to other scripts.
 #
 #
 # Args/Kwargs Notes:
 #      Array (args):
 #          Access all args with "${args[@]}"
 #
 #      Dict (kwargs):
 #          Access all keys with "${!kwargs[@]}".
 #          Access all values with "${kwargs[@]}".
 #
 #      Check if contains with =~
 #          Ex: "${args[@]}" =~ "-h" to check if args contains "-h".
 #
 #
 # Color Notes:
 #      Use colors by adding the "-e" flag to echo, otherwise it will just print out the ascii values of the color.
 #
 #      Reset - Should be used at the end of every echo that uses a color.
 #      Red - For errors.
 #      Green - For success notifications.
 #      Blue - Headers to visually differentiate new sections of data to the user.
 #      Cyan - For prompts that ask the user to input a value.
 #
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
 # To set a value as a kwarg (key, value pair), first define a "key_value_args" array before calling the this function.
 # Any values inside this "key_value_args" array will be considered a key. When these key args are found, the argument
 # immediately following is considered to be the associated value.
 #
 # If two keys occur in a row, or a key occurs with no value following, then an error will raise.
 #
 # https://opensource.com/article/18/5/you-dont-know-bash-intro-bash-arrays
 # https://stackoverflow.com/a/3467959
 ##
function parse_args () {
    key=""
    for arg in $orig_args
    do
        # Check if we already have a key.
        if [[ $key != "" ]]
        then

            # We have a key. Check that we don't have two in a row.
            if [[ ! ${#key_value_args[@]} -eq 0 && ${key_value_args[@]} =~ $arg ]]
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
            # Key value pairs must be manually established by being defined in key_value_args.
            if [[ ! ${#key_value_args[@]} -eq 0 && ${key_value_args[@]} =~ $arg ]]
            then
                # Handle for kwarg key.
                key=${arg}
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
        exit 1
    fi
}


###
 # Prints all args and kwargs to console.
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

        orig_key=$key
        echo "Kwargs:"
        for key in ${!kwargs[@]}
        do
            echo "    $key: ${kwargs[$key]}"
        done
        key=$orig_key
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
            exit 1
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
        exit 1
    fi

    # Check that users match.
    if [[ "$USER" != "$1" ]]
    then
        echo ""
        echo -e "${color_red}Please run script as \"$1\" user. Terminating script.${color_reset}"
        echo ""
        exit 1
    fi
}


###
 # Checks that user does NOT match provided argument.
 ##
function check_not_user () {
    # Check that user value was provided by first arg.
    if [[ "$1" == "" ]]
    then
        echo ""
        echo -e "${color_red}No user passed in to \"check_user\" function. Terminating script.${color_reset}"
        echo ""
        exit 1
    fi

    # Check that users do not match.
    if [[ "$USER" == "$1" ]]
    then
        echo ""
        echo -e "${color_red}Please do not run script as \"$1\" user. Terminating script.${color_reset}"
        echo ""
        exit 1
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


###
 # Checks for help flags of "-h" or "--help".
 # If present, sets "help_flag" variable to true.
 ##
function check_for_help_flags () {
    help_flag=false
    new_args=()

    # Examine all args.
    for arg in ${args[@]}
    do
        # Check if help flag.
        if [[ $arg == "-h" || $arg == "--help" ]]
        then
            # Help flag found.
            help_flag=true
        else
            # Not help flag. Preserve value for later.
            new_args+=($arg)
        fi
    done

    # Update args.
    args=(${new_args[@]})
    new_args=""
}


# Process all args.
parse_args
