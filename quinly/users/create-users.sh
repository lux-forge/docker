# This script will create the necessary user accounts in the Docker containers.


function create_user(){
  $new_user = $1
  $id = $2
  $setPassword = $3
  $isAdmin = $4
  # Set the username
  if [ -z "$new_user" ]; then
    echo "Enter the username:"
    read new_user
  fi

# Delete the user if already exists
  echo "Deleting user:$new_user if it exists..."
  if id $new_user &>/dev/null; then
      echo "User $new_user exists." 
      sudo userdel -r $new_user
      echo "User $new_user has been deleted. Removing home dirs"
      sudo rm /home/$new_user -R
  else
      echo "User $new_user does not exist."
  fi

  echo "Creating user..."
  # If there is an ID, create a group
  if [ -n "$id" ]; then
    echo "Creating group with ID $id..."
    sudo groupadd -g $id -m $new_user -s /bin/bash 
  else
      sudo useradd -m $new_user -s /bin/bash 
  fi

  echo "User $new_user created successfully. With home directory at /home/$new_user"

  # Set the password
  if $setPassword; then
    echo "Setting password for user $new_user..."
    sudo passwd $new_user
    echo "Password for user $new_user set successfully."
  fi


  # Adding groups
  if $isAdmin; then
    for group in adm cdrom sudo dip plugdev lxd docker; do
        echo "Adding user $new_user to $group"
        sudo usermod -aG $group $new_user
    done
  fi
}
while IFS="," read -r name id
do
  create_user $name $id false false
done < <(tail -n +2 users.csv)