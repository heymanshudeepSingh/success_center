#!/usr/bin/env bash
# Script to install MariaDB (a MySQL equivalent) dependencies on a Arch Linux system.


return_value=""
color_reset='\033[0m'
color_red='\033[1;31m'
color_green='\033[1;32m'
color_blue='\033[1;34m'
color_cyan='\033[1;36m'


function main() {

    # Make sure we are root.
    if [ "$USER" != "root" ]
    then
        echo ""
        echo -e "${color_red}Please run script as sudo user. Terminating script.${color_reset}"
        echo ""
        exit 0
    fi

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

    # Set extra database config values.
    # Note that mysql "utf8" is apparently only encoded in 3 bytes per character. Real utf8 is 4 bytes per.
    # To fix this, mysql "utf8mb4" was introduced that follows proper utf8 encoding standards.
    # See https://medium.com/@adamhooper/in-mysql-never-use-utf8-use-utf8mb4-11761243e434 for more info.
    echo "" >> /etc/mysql/my.cnf
    echo "#" >> /etc/mysql/my.cnf
    echo "# Set default character set." >> /etc/mysql/my.cnf
    echo "#" >> /etc/mysql/my.cnf
    echo "[client]" >> /etc/mysql/my.cnf
    echo "default-character-set = utf8mb4" >> /etc/mysql/my.cnf
    echo "" >> /etc/mysql/my.cnf
    echo "[mysqld]" >> /etc/mysql/my.cnf
    echo "collation_server = utf8mb4_unicode_ci" >> /etc/mysql/my.cnf
    echo "character_set_server = utf8mb4" >> /etc/mysql/my.cnf
    echo "" >> /etc/mysql/my.cnf
    echo "[mysql]" >> /etc/mysql/my.cnf
    echo "default-character-set = utf8mb4" >> /etc/mysql/my.cnf
    echo "" >> /etc/mysql/my.cnf

    echo "" >> /etc/mysql/my.cnf
    echo "#" >> /etc/mysql/my.cnf
    echo "# Allow auto-completion in MySQL client." >> /etc/mysql/my.cnf
    echo "#" >> /etc/mysql/my.cnf
    echo "auto-rehash" >> /etc/mysql/my.cnf
    echo "" >> /etc/mysql/my.cnf

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
