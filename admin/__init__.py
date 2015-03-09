""" mupy web admin """
from os.path import dirname
from flask import Flask
from flask.ext.mongoengine import MongoEngine

OUTPUT_FOLDER = '/var/www/mupy/output'

app = Flask(__name__)

app.debug = True

app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['ABSOLUTE_PATH'] = dirname(__file__)
app.config['MONGODB_DB'] = 'mupy'
app.secret_key = '\xe8\xb0\xce\x13\xe0\xaeR\xccVj\xc2\xf7S\xbe\xc8\x1d`\xfa\x13zF\xe2z\xfe'

db = MongoEngine(app)

import admin.views
