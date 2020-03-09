#!/usr/bin/env bash
# Import utility script.
source $(dirname $0)/../utils.sh

function main(){
    echo -e "${color_cyan}Enter your email:${color_reset}"
    read email
    echo -e "${color_cyan}Enter your BroncoNet ID:${color_reset}"
    read wmu_ID

    if [[ -d ~/.ssh ]]
        then
            cd ~/.ssh/
        else
            cd ~/
            mkdir ".ssh"
            cd .ssh
    fi

    loop=true

while [[ "$loop" == true ]]
  do
      echo "Enter OS type:"
          echo -e "   ${color_cyan}1${color_reset}) Ubuntu 16.04"
          echo -e "   ${color_cyan}2${color_reset}) Ubunutu 18.04"
          echo -e "   ${color_cyan}3${color_reset}) Other"
          read user_input
          echo ""
          echo ""

          # check for ubuntu 16.04
          if [[ "$user_input" == "1" ]]
          then
              generate_rsa
              loop=false

          # Ubuntu.
          elif [[ "$user_input" == "2" ]]
          then
              generate_ed255
              loop=false

          # any other OS types
          elif [[ "$user_input" == "3" ]]
          then

              echo -e "${color_red}Sorry, this script does not currently support any other OS types.${color_reset}"
              echo "Exiting script."
              exit 0
          else
              echo -e "${color_red}Invalid input.${color_reset}"
          fi
      done
      echo -e "${color_blue}Hit enter to continue... ${color_reset}"
      read
      ssh -T git@git.ceas.wmich.edu

}
# For Ubuntu 16.04
function generate_rsa () {
    if [[ -f cae_gitlab_rsa ]]
        then
            echo "removing existing ssh key..."
            rm -r cae_gitlab_rsa*
        else
            echo "Creating new ssh key..."
        fi
    echo "/home/$USER/.ssh/cae_gitlab_rsa" | ssh-keygen -o -t rsa -b 4096 -C "$email"
    config_file=config
    config_content=$(cat $config_file)
    if [[ $config_content == *"git.ceas.wmich.edu"* ]]; then
        echo "config file is already updated!"
    else
        echo "" >> $config_file
        echo "#" >> $config_file
        echo "Host git.ceas.wmich.edu" >> $config_file
        echo "	User $wmu_ID" >> $config_file
        echo "	IdentityFile /home/$USER/.ssh/cae_gitlab_rsa" >> $config_file
        echo "" >> $config_file
        echo ""
        echo "Updated Config!"
    fi
    ssh-add cae_gitlab_rsa
    echo ""
    echo -e "${color_blue}Copy this public key into your gitlab ${color_reset}"
    echo ""
    cat cae_gitlab_rsa.pub
    echo ""
}

function generate_ed255() {

    if [[ -f cae_gitlab_ed255 ]]
    then
        echo "removing existing ssh key..."
        rm -r cae_gitlab_ed255*
    else
        echo "Creating new ssh key..."
    fi
    echo "/home/$USER/.ssh/cae_gitlab_ed255" | ssh-keygen -t ed25519 -C "$email"
    config_file=config
    config_content=$(cat $config_file)

    if [[ $config_content == *"git.ceas.wmich.edu"* ]]; then
        echo "config file is already updated!"
    else
        echo "#" >> $config_file
        echo "Host git.ceas.wmich.edu" >> $config_file
        echo "	User $wmu_ID" >> $config_file
        echo "	IdentityFile /home/$USER/.ssh/cae_gitlab_ed255" >> $config_file
        echo "" >> $config_file
        echo ""
        echo "Updated Config!"
    fi
        ssh-add cae_gitlab_ed255
        echo ""
        echo -e "${color_blue}Copy this public key into your gitlab ${color_reset}"
        echo ""
        cat cae_gitlab_ed255.pub
        echo ""

}
main

