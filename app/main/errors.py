from flask import render_template
from werkzeug.exceptions import HTTPException

from . import main


@main.errorhandler(HTTPException)
def handle_exception(e):
    return render_template('error.html', status_code=e.code, error_message=e.name)
