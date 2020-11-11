#!/bin/bash
###
 # Script to reset database, including fresh, uncommitted migrations.
 # Currently only works with sqlite databases.
 ##


# Abort on error
set -e


# Import utility script.
source $(dirname $0)/../utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


function main () {
    # Remove migrations.
    ./development/reset_migrations.sh force

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

    # Check for debug file.
    if [[ -f "../DEBUG" ]]
    then
        # Development environment. Create seeded data. Attempts to used passed model_count arg.
        echo -e "${color_blue}Seeding data...${color_reset}"

        model_count="$1"
        re='^[0-9]+$'
        if ! [[ $model_count =~ $re ]]
        then
            python ../manage.py seed $model_count --traceback
        else
            python ../manage.py seed --traceback
        fi
        echo ""
        echo -e "${color_green}Database reset and reseeded. Terminating script.${color_reset}"
    else
        # Production environment. Skip seeds.
        echo -e "${color_green}Database reset. Terminating script.${color_reset}"
    fi


}


# Warn user with prompt. Skips if arg of "force" was provided.
if [[ ! ${args[@]} =~ "force" ]]
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
        main "${args[0]}"
    fi

else
    # Force command provided. Skipping prompt.
    # First remove arg as it's no longer necessary.
    args=${args[@]#force}
    main "${args[0]}"
fi
