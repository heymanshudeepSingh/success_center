#!/usr/bin/env bash
# Script for first time setup of project.


return_value=""
color_reset='\033[0m'
color_red='\033[1;31m'
color_green='\033[1;32m'
color_blue='\033[1;34m'
color_cyan='\033[1;36m'


# Change to location of script's directory.
# Otherwise logic is inconsistent, based on where terminal initially is.
cd "$(dirname "$0")/../.."


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


function main() {
    # Make sure we are root.
    if [ "$USER" == "root" ]
    then
        echo ""
        echo -e "${color_red}Please do not run script as sudo user. Terminating script.${color_reset}"
        echo ""
        exit 0
    else
        echo ""
        echo "Note: This script will run first time project setup."
        echo "      To cancel, hit ctrl+c now. Otherwise hit enter to start."
        read user_input
    fi

    user_confirmation "Run project in development mode?"
    if [[ "$return_value" = true ]]
    then
        touch DEBUG
        echo "To run in production, delete the \"DEBUG\" file located at project root."
    else
        echo "To run in development, create an empty file called \"DEBUG\" at project root."
    fi
    echo ""

    cp ./settings/local_env/env_example.py ./settings/local_env/env.py

    loop=true
    while [[ "$loop" == true ]]
    do
        echo "Enter OS type:"
        echo "   1) Arch Linux"
        echo "   2) Ubunutu Linux"
        echo "   3) Other"
        read user_input
        echo ""
        echo ""

        # Arch linux (manjaro).
        if [[ "$user_input" == "1" ]]
        then
            echo -e "NOTE: This script has been tested on ${color_blue}Manjaro XFCE 18.0.4${color_reset}."
            echo "The script will ask for your password in a second..."
            echo ""
            echo -e "${color_blue}Installing ArchLinux package dependencies...${color_reset}"
            sudo ./scripts/installers/arch_install.sh
            echo ""
            loop=false

        # Ubuntu.
        elif [[ "$user_input" == "2" ]]
        then
            echo -e "NOTE: This script has been tested on ${color_blue}Ubuntu Desktop 16.04${color_reset}."
            echo "This script will ask for your password in a second..."
            echo ""
            echo -e "${color_blue}Installing Ubuntu package dependencies...${color_reset}"
            sudo ./scripts/installers/ubuntu_install.sh
            echo ""
            loop=false

        # Unsupported OS.
        elif [[ "$user_input" == "3" ]]
        then
            echo -e "${color_red}Sorry, this script does not support any other OS types.${color_reset}"
            echo "To proceed:"
            echo "   * Load your desired python environment and install from requirements.txt."
            echo "      (This may require additional OS packages, depending on your system.)"
            echo "   * Run the standard Django manage.py commands."
            echo "      (\"makemigrations\", \"migrate\", and optionally \"seed\", in that order.)"
            echo "   * Install \"ruby-sass\" and then run the \"compile_css.sh\" file in the project scripts folder."
            echo "   * Install selenium (integration testing) dependencies for your system."
            echo "   * Run \"python manage.py test\" to ensure that everything is working properly."
            echo ""
            echo "If all tests pass, then the project has installed successfully."
            echo "(If you got this far, consider updating these scripts to support the OS you used.)"
            echo ""
            echo "Exiting script."
            exit 0
        else
            echo -e "${color_red}Invalid input.${color_reset}"
        fi
    done


    # Compile CSS.
    echo -e "${color_blue}Compiling CSS files...${color_reset}"
    sudo ./scripts/compile_css.sh
    echo ""


    # Attempt to set up Python for user.
    user_confirmation "Install local python environment in project root?"
    if [[ "$return_value" == true ]]
    then
        # Get Python version. Should be in format of "#.#".
        valid_python=""
        python_version=""

        while [[ ! $valid_python ]]
        do
            echo "Enter Python version for Project (Must be Python 3.6 or higher):"
            read user_input
            if [[ $user_input = "3.6" ]] || [[ $user_input = "3.7" ]] || [[ $user_input = "3.8" ]]
            then
                echo ""
                valid_python=true
                python_version=$user_input
            else
                echo "Invalid input. Please enter version, such as \"3.6\" or \"3.7\"."
                echo ""
            fi
        done

        # Create environment with desired python version.
        echo -e "${color_blue}Installing local environment...${color_reset}"
        "python$python_version" -m venv .venv

        # Install python requirements.
        echo -e "${color_blue}Installing python requirements...${color_reset}"
        echo ""
        source ./.venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        echo ""
        echo -e "${color_blue}If you wanted MySQL or LDAP, please uncomment the appropriate lines in requirements.txt and rerun \"pip install -r requirements.txt\".${color_reset}"
        echo ""

        # Create initial database.
        python manage.py makemigrations
        python manage.py migrate
        echo ""
        echo -e "${color_blue}SQLite database created. To use MySQL or PostreSQL, change the settings in \"settings/local_env/env.py\" and rerun \"python manage.py migrate\".${color_reset}"
        echo ""

        user_confirmation "Create initial seed for database?"
        if [[ $return_value == true ]]
        then
            echo "Enter model seed count (default is 100)."
            read user_input
            echo ""
            echo -e "${color_blue}Seeding database...${color_reset}"
            python manage.py seed $user_input
            echo ""
        else
            echo -e "${color_blue}Skipping database seed, but still loading initial fixtures...${color_reset}"
            python manage.py loadfixtures
            echo ""
        fi

        echo -e "${color_blue}Everything set up. Now running project tests...${color_reset}"
        echo ""
        python manage.py test

        deactivate

    # Unknown Python environment.
    else
        echo "No local Python environment found at project root. Script cannot continue."
        echo "To proceed:"
        echo "   * Load your desired python environment and install from requirements.txt."
        echo "   * Run the standard Django manage.py commands."
        echo "      (\"makemigrations\", \"migrate\", and optionally \"seed\", in that order.)"
        echo "   * Install \"ruby-sass\" and then run the \"compile_css.sh\" file in the project scripts folder."
        echo "   * Install selenium (integration testing) dependencies for your system."
        echo "   * Run \"python manage.py test\" to ensure that everything is working properly."
        echo ""
        echo "If all tests pass, then the project has installed successfully."
    fi

    echo ""
    echo "Exiting script."
    exit 0
}


main
