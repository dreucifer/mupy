""" mupy web admin """
from flask import Flask
from admin.database import db_session

app = Flask(__name__)

import admin.views


@app.teardown_appcontext
def shutdown_dbsession(exception=None):
    db_session.remove()
