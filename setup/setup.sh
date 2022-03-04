#!/usr/bin/env bash

# install requirements
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install apache2 mysql-client mysql-server
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update

# python is already usually installed on ubuntu, so just install pip
sudo apt install python3-pip

# wsgi
sudo apt-get install apache2 apache2-dev

# requirements
pip3 install -r requirements/local.txt
pip3 install -r requirements/server.txt

# linux only requirements
pip3 install mod_wsgi
pip3 install mysqlclient

# mysql for python
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
sudo apt-get install python3-pymysql

# certbot
sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update

sudo apt-get install certbot python3-certbot-apache

# setup git hub
git config user.email "naveen.ailawadi91@gmail.com"
git config user.name "Naveen Ailawadi"

# add digital ocean metrics
curl -sSL https://repos.insights.digitalocean.com/install.sh | sudo bash

# full docs: https://pythonprogramming.net/basic-flask-website-tutorial/
# will need these ^ to set up the manual stuff
