$env:FLASK_APP='app'

flask db init
flask db migrate
flask db upgrade
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\manage.py
