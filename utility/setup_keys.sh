#!/usr/bin/env bash

if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -f ~/.ssh/id_rsa -t rsa -N ""
fi

echo "Add following public key to the git repository deploy keys:"
echo "-------------------------------------------------------------------"
cat ~/.ssh/id_rsa.pub
echo "-------------------------------------------------------------------"


echo "Enter the public key to add in authorized_keys:"
read public_key

if [ ${#public_key} ]; then
    echo "$public_key" >> ~/.ssh/authorized_keys
    echo "Key added"
else
    echo "No key provided"
fi
