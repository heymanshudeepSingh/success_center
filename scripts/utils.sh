#!/usr/bin/env bash
###
 # Utility/helper logic for other scripts. Impriting this file imports all logic, callable as functions.
 # Version 1.0
 #
 #
 # return_value:
 #  * Used to save the return values of functions.
 #  * Normal return values only let us return "error codes", aka integers. Any integer other than 0 will count as an
 #    "error flag" and cause the scripts to terminate if the "set -e" flag is set.
 #
 #
 # Color Notes:
 #  * Colors variables are used to change color of text displayed to console.
 #  * Use colors by adding the "-e" flag to echo, otherwise it will just print out the ascii values of the color.
 #  * Intended main use cases for colors are as follows:
 #      * Reset - Should be used at the end of every echo that uses a color.
 #      * Red - For errors.
 #      * Green - For success notifications.
 #      * Blue - Headers to visually differentiate new sections of data to the user.
 #      * Cyan - For prompts that ask the user to input a value.
 #
 #
 # Args/Kwargs Notes:
 #  * Array (args):
 #      * Access all args with "${args[@]}".
 #      * All original passed values which are not interpreted as a kwarg will be considered an arg.
 #
 #  * Dict (kwargs):
 #      * Access all keys with "${!kwargs[@]}".
 #      * Access all values with "${kwargs[@]}".
 #      * To interpret a value pairing as a kwarg:
 #          * Define an array variable called "key_value_args" before importing this util script.
 #          * In said array, define all possible args to read in as dictionary keys.
 #              * Ex: key_value_args=("my_key_1", "my_key_2")
 #          * On execution, if one of these keys is found, then the direct next arg will be interpreted as the
 #            associated value.
 #
 #  * Check if contains with =~
 #      * Ex: "${args[@]}" =~ "-h" to check if args array contains value "-h".
 #
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


#region General Helper Functions

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

    # Get user's input.
    echo -e "$1 ${color_cyan}[ Yes | No ]${color_reset}"
    read user_input

    # Convert to lower case.
    if [[ $user_input != "" ]]
    then
        string_to_lower $user_input
    else
        return_value=""
    fi

    # Check user value.
    if [[ "$return_value" = "yes" ]] || [[ "$return_value" = "ye" ]] || [[ "$return_value" = "y" ]]
    then
        return_value=true
    else
        return_value=false
    fi
}


###
 # Converts string to upper case.
 ##
function string_to_upper () {
    if [[ $1 != "" ]]
    then
        return_value="$(echo $1 | tr [':lower:'] [':upper:'])"
    else
        echo -e "${color_red}No value was passed. Cannot convert to upper case.${color_reset}"
        return_value=""
    fi
}


###
 # Converts string to lower case.
 ##
function string_to_lower () {
    if [[ $1 != "" ]]
    then
        return_value="$(echo $1 | tr [':upper:'] [':lower:'])"
    else
        echo -e "${color_red}No value was passed. Cannot convert to lower case.${color_reset}"
        return_value=""
    fi
}


#endregion General Helper Functions


#region Directory Management Functions

###
 # Changes the location of terminal instance to the same directory the calling script file resides in.
 # Lasts until script ends or another cd command is used.
 # Can help make logic more consistent, if location of terminal matters.
 ##
function normalize_directory () {
    cd "$(dirname "$0")"
}


###
 # Change location of script's directory to the project's top level "scripts" folder, if it exists.
 # Can help make logic more consistent, if location of terminal matters.
 # May be more reliable than "normalize_directory" function, in cases where the scripts directory is large and has
 # multiple levels.
 ##
function change_to_scripts_directory () {
    # First normalize directory, so it doesn't matter where we called from in terminal.
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
 # Gets absolute path of provided file/directory.
 ##
function get_absolute_path () {
    # First check if valid file or directory.
    if [[ -d $1 || -f $1 ]]
    then
        return_value="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
    else
        echo -e "${color_red}Passed value ($1) does not appear to be a file or directory.${color_reset}"
        return_value=""
    fi
}

#endregion Directory Management Functions



#region Arg Parsing/Management Functions

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

    # Loop through all the original passed args.
    for arg in $orig_args
    do
        # Check if we already have a key.
        if [[ $key != "" ]]
        then
            # Value is a key.

            # Check that we don't have two keys in a row.
            if [[ ! ${#key_value_args[@]} -eq 0 && ${key_value_args[@]} =~ $arg ]]
            then
                # Found a second key immediately after the first.
                echo ""
                echo -e "${color_red}Two keys were passed in a row. Expected key, value pairs. Terminating script.${color_reset}"
                echo ""
                exit 1
            fi

            # Save key value pair.
            kwargs[$key]=$arg

            # Reset key.
            key=""
        else
            # Value is not a key.

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

#endregion Arg Parsing/Management Functions


# Process all args.
parse_args
