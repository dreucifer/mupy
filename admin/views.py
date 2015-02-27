""" views for mupy web admin """
from os.path import join
from admin import app


@app.route('/')
def index():
    """ Main page """
    return "Hello World"


@app.route('/add')
def add_page():
    """ add a new page """
    return "@todo: Create add page"


@app.route('/edit/<slug>')
def edit_page(slug):
    """ edit a page """
    return "@todo: Create edit page %s" % slug


@app.route('/js/<path:path>')
def javascript(path):
    """ Serve up javascript """
    return app.send_static_file(join('js', path))
