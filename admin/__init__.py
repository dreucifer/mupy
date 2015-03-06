""" mupy web admin """
from os.path import dirname
from flask import Flask
from admin.database import db_session

OUTPUT_FOLDER = '/var/www/mupy/output'

app = Flask(__name__)

app.debug = True
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['ABSOLUTE_PATH'] = dirname(__file__)
app.secret_key = '\xe8\xb0\xce\x13\xe0\xaeR\xccVj\xc2\xf7S\xbe\xc8\x1d`\xfa\x13zF\xe2z\xfe'

import admin.views


@app.teardown_appcontext
def shutdown_dbsession(exception=None):
    db_session.remove()
