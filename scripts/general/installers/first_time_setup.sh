#!/usr/bin/env bash
###
 # Script for first time setup of project.
 ##


# Import utility script.
source $(dirname $0)/../../utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


function main() {
    # Make sure we are root.
    check_not_user "root"

    # Display friendly prompt to user.
    echo ""
    echo "Note: This script will run first time project setup."
    echo -e "      ${color_cyan}To cancel, hit ctrl+c now. Otherwise hit enter to start.${color_reset}"
    read user_input

    user_confirmation "Run project in development mode?"
    if [[ "$return_value" = true ]]
    then
        touch DEBUG
        echo "To run in production, delete the \"DEBUG\" file located at project root."
    else
        echo "To run in development, create an empty file called \"DEBUG\" at project root."
    fi
    echo ""

    cp ../settings/local_env/env_example.py ../settings/local_env/env.py

    loop=true
    windows=false
    while [[ "$loop" == true ]]
    do
        echo "Enter OS type:"
        echo -e "   ${color_cyan}1${color_reset}) Arch Linux"
        echo -e "   ${color_cyan}2${color_reset}) Ubunutu Linux"
        echo -e "   ${color_cyan}3${color_reset}) Windows 10"
        echo -e "   ${color_cyan}4${color_reset}) Other"
        read user_input
        echo ""
        echo ""

        # Arch linux (such as Manjaro).
        if [[ "$user_input" == "1" ]]
        then
            echo -e "NOTE: This script has been tested on ${color_blue}Manjaro XFCE 18.0.4${color_reset}."
            echo "The script will ask for your password in a second..."
            echo ""
            echo -e "${color_blue}Installing ArchLinux package dependencies...${color_reset}"
            sudo ./general/installers/arch_install.sh
            echo ""
            loop=false

        # Ubuntu.
        elif [[ "$user_input" == "2" ]]
        then
            echo -e "NOTE: This script has been tested on ${color_blue}Ubuntu Desktop 16.04${color_reset}."
            echo "This script will ask for your password in a second..."
            echo ""
            echo -e "${color_blue}Installing Ubuntu package dependencies...${color_reset}"
            sudo ./general/installers/ubuntu_install.sh
            echo ""
            loop=false

        # Windows 10.
        elif [[ "$user_input" == "3" ]]
        then
            echo -e "NOTE: This script has been tested on ${color_blue}Windows 10, with updates for 2019${color_reset}."
            echo -e "If you haven't already done so, please install Python Version 3.6 or higher from ${color_cyan}https://www.python.org/downloads/${color_reset}."
            echo ""
            echo "Please also follow the link below to download ruby."
            echo -e "   ${color_cyan}https://rubyinstaller.org/downloads/${color_reset}"
            echo -e "Run the ruby exe installer. Once ruby is already installed, hit ${color_blue}ENTER${color_reset} to continue."
            echo "(You may first need to restart your terminal for it to dectect that ruby is installed.)"
            echo ""
            read user_input
            gem install sass
            echo ""
            windows=true
            loop=false

        # Unsupported OS.
        elif [[ "$user_input" == "4" ]]
        then
            echo -e "${color_red}Sorry, this script does not currently support any other OS types.${color_reset}"
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
    if [[ "$windows" == true ]]
    then
        ./general/compile_css.sh
    else
        sudo ./general/compile_css.sh
    fi
    echo ""


    # Attempt to set up Python for user.
    user_confirmation "Install local python environment in project root?"
    if [[ "$return_value" == true ]]
    then
        cd ..

        # Get Python version. Should be in format of "#.#".
        valid_python=""
        python_version=""

        # Loop until user provides a valid version of Python.
        while [[ ! $valid_python ]]
        do
            echo "Enter Python version for Project (Must be Python 3.6 or higher):"
            read user_input
            if [[ $user_input = "3.6" ]] || [[ $user_input = "3.7" ]] || [[ $user_input = "3.8" ]] || [[ $user_input == "3.9" ]]
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
        if [[ "$windows" == true ]]
        then
            python -m venv .venv
        else
            "python$python_version" -m venv .venv
        fi

        # Install python requirements.
        echo -e "${color_blue}Installing python requirements...${color_reset}"
        echo ""
        if [[ "$windows" == true ]]
        then
            . ./.venv/Scripts/activate
            python -m pip install --upgrade pip
            pip install pywin32
            pip install -r requirements.txt
        else
            source ./.venv/bin/activate
            pip install --upgrade pip
            pip install -r requirements.txt
        fi
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

        echo ""
        echo "If all tests passed, then the project has installed successfully."

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
        echo "If all tests pass, then the project installed successfully."
    fi


    echo ""
    echo "Exiting script."
    exit 0
}

main