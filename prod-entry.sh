#!/bin/bash

wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb
sudo dpkg -i wkhtmltox_0.12.5-1.bionic_amd64.deb
sudo apt install -f

export FLASK_APP='app' 

pip install -r requirements.txt

echo "Appling database migrations..."
flask db init
flask db migrate
flask db upgrade

