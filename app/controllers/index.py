from flask import render_template, Blueprint

blueprint = Blueprint('main', __name__)

@blueprint.route('/')
@blueprint.route('/home')
def home():
    return render_template('index.html')

