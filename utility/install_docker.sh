#!/usr/bin/env bash
# https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-using-the-repository
echo "Run update packages list..."
apt-get update

echo "Install libraries..."
apt-get install apt-transport-https ca-certificates curl software-properties-common

echo "Download & add docker repository key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

echo "Run update packages list..."
apt-get update

echo "Install docker..."
apt-get install docker-ce

echo "Install compose..."
curl -L https://github.com/docker/compose/releases/download/1.16.1/docker-compose-`uname -s`-`uname -m` > docker-compose
chmod +x docker-compose
mv docker-compose /usr/local/bin
