#!/usr/bin/env bash
###
 # Script to install MariaDB (a MySQL equivalent) dependencies on a Arch Linux system.
 ##


# Import utility script.
source $(dirname $0)/../../../utils.sh


# Standardize current terminal path to project "scripts" directory.
change_to_scripts_directory


function main() {

    # Make sure we are root.
    check_user "root"

    echo "Installing MariaDB (a MySQL equivalent) for Arch Linux..."

    # Install mysql.
    pacman -S mysql --noconfirm

    # Setup initial mysql config.
    mysql_install_db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
    systemctl enable mariadb.service
    systemctl start mariadb.service

    # Run mysql secure installation for full setup.
    mysql_secure_installation

    # Set proper permissions.
    chown mysql:root -R /var/lib/mysql
    find /var/lib/mysql -type d -exec chmod g+rwx {} \;
    chmod g+rw -R /var/lib/mysql

    # Check for location of "my.cnf" file on system.
    config_file=""
    if [[ -f /etc/mysql/my.cnf ]]
    then
        config_file="/etc/mysql/my.cnf"
    elif [[ -f /etc/my.cnf ]]
    then
        config_file="/etc/my.cnf"
    else
        echo -e "${color_red}Could not find \"my.cnf\" file at either /etc/mysql or /etc directories.${color_reset}"
        echo -e "${color_red}Config values cannot be set without a \"my.cnf\" file.${color_reset}"
        echo -e "${color_red}Please check if any errors have occured before this point and try again.${color_reset}"
        echo -e "${color_red}Terminating script.${color_reset}"
        exit 0
    fi

    echo ""
    echo -e "${color_blue}Initial DB installation complete.${color_reset}"
    echo -e "${color_blue}Setting up config located at \"$config_file\".${color_reset}"

    # Set extra database config values.
    # Note that mysql "utf8" is apparently only encoded in 3 bytes per character. Real utf8 is 4 bytes per.
    # To fix this, mysql "utf8mb4" was introduced that follows proper utf8 encoding standards.
    # See https://medium.com/@adamhooper/in-mysql-never-use-utf8-use-utf8mb4-11761243e434 for more info.
    echo "" >> $config_file
    echo "#" >> $config_file
    echo "# Set default character set." >> $config_file
    echo "#" >> $config_file
    echo "[client]" >> $config_file
    echo "default-character-set = utf8mb4" >> $config_file
    echo "" >> $config_file
    echo "[mysqld]" >> $config_file
    echo "collation_server = utf8mb4_unicode_ci" >> $config_file
    echo "character_set_server = utf8mb4" >> $config_file
    echo "" >> $config_file
    echo "[mysql]" >> $config_file
    echo "default-character-set = utf8mb4" >> $config_file
    echo "" >> $config_file

    echo "" >> $config_file
    echo "#" >> $config_file
    echo "# Allow auto-completion in MySQL client." >> $config_file
    echo "#" >> $config_file
    echo "auto-rehash" >> $config_file
    echo "" >> $config_file

    # Restart database to read in modified setup.
    systemctl restart mariadb.service

    # Install python mysql dependencies.
    pacman -S python-mysqlclient --noconfirm

    # Success. Exit script.
    echo ""
    echo -e "${color_green}Installation has finished. Terminating Arch MariaDb script.${color_reset}"
    exit 0
}


main
