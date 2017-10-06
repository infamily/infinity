#!/usr/bin/env bash
# https://certbot.eff.org/#ubuntuxenial-nginx
apt-get update
apt-get install -y software-properties-common
add-apt-repository -y ppa:certbot/certbot
apt-get update
apt-get install -y python-certbot-nginx

# we should to remove nginx because using dockerized one
apt-get remove -y nginx
