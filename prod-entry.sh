#!/bin/bash
export FLASK_APP='app' 
pip install -r requirements.txt
echo "Appling database migrations..."
flask db init
flask db migrate
flask db upgrade

