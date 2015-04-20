""" mupy web admin """
from os.path import dirname
from flask import Flask
from flask.ext.admin import Admin, AdminIndexView
from flask.ext.mongoengine import MongoEngine
from flask.ext.babel import Babel

OUTPUT_FOLDER = '/var/www/mupy/output'

app = Flask(__name__)

app.debug = True

app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['ABSOLUTE_PATH'] = dirname(__file__)
app.config['MONGODB_DB'] = 'mupy'
app.secret_key = '\xe8\xb0\xce\x13\xe0\xaeR\xccVj\xc2\xf7S\xbe\xc8\x1d`\xfa\x13zF\xe2z\xfe'

db = MongoEngine(app)
babel = Babel(app)
admin = Admin(
    app,
    template_mode='bootstrap3',
    index_view=AdminIndexView(
        name="Home",
        template="admin_index.html"
    )
)

import mupy_admin.views
import mupy_admin.filters
