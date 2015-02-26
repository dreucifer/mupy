""" mupy web admin """
from flask import Flask
app = Flask(__name__)

import admin.views

from admin.database import db_session

@app.teardown_appcontext
def shutdown_dbsession(exception=None):
    db_session.remove()
