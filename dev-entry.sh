#!/bin/bash
export FLASK_APP='app' 
echo "Appling database migrations..."
flask db init
flask db migrate
flask db upgrade
./manage.py
