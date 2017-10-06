#!/usr/bin/env bash
# https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-using-the-repository
echo "Run update packages list..."
apt-get update

echo "Install libraries..."
apt-get install -y apt-transport-https ca-certificates curl software-properties-common

echo "Download & add docker repository key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

echo "Run update packages list..."
apt-get update

echo "Install docker..."
apt-get install -y docker-ce

echo "Install python-pip..."
apt-get install -y python-pip
export LC_ALL=C

echo "Upgrade python..."
pip install --upgrade pip

echo "Install docker-py"
pip install docker>=2.0.1

echo "Install docker-compose"
pip install docker-compose>=1.16.1
