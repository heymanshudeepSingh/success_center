#!/bin/bash
# Script to reset database, including fresh migrations.
# Currently only works with sqlite databases.


# Abort on error
set -e


# Global Variables.
return_value=""
color_reset='\033[0m'
color_red='\033[1;31m'
color_green='\033[1;32m'
color_blue='\033[1;34m'
color_cyan='\033[1;36m'


# Get passed script args.
model_count="$1"


# Change to location of script's directory.
# Otherwise logic is inconsistent, based on where terminal initially is.
cd "$(dirname "$0")"


###
 # Display passed prompt and get user input.
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


function main () {
    # Remove migrations.
    ./reset_migrations.sh force

    # Remove sqlite database if present.
    rm -f ../db.sqlite3

    # Activate venv if present.
    if [[ -d "../.venv" ]]
    then
        . ../.venv/bin/activate
    fi

    # Recreate migrations.
    echo ""
    echo ""
    echo -e "${color_blue}Creating migrations...${color_reset}"
    python ../manage.py makemigrations
    echo ""
    echo ""
    echo ""

    # Migrate.
    echo -e "${color_blue}Migrating to database...${color_reset}"
    python ../manage.py migrate
    echo ""
    echo ""
    echo ""

    # Create seeded data. Attempts to used passed model_count arg.
    echo -e "${color_blue}Seeding data...${color_reset}"

    re='^[0-9]+$'
    if ! [[ $yournumber =~ $re ]]
    then
        python ../manage.py seed $model_count --traceback
    else
        python ../manage.py seed --traceback
    fi
    echo ""

    echo -e "${color_green}Database reset and reseeded. Terminating script.${color_reset}"
}


# Warn user with prompt. Skips if arg of "force" was provided.
if [[ $1 != "force" ]]
then
    echo ""
    echo "Note: This will remove all migrations in CAE_Workspace, including ones in the apps subfolders."
    echo "      It will also reset and reseed the database, removing any previously existing data."
    echo "      This script probably shouldn't be run in production environments."
    echo "      Only proceed if you know what you are doing."
    echo ""

    user_confirmation "Are you sure you want to DELETE AND RESET?"

    if [[ "$return_value" == true ]]
    then
        echo ""
        echo ""
        main
    fi

    exit
else
    main
fi
