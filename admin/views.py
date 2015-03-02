""" views for mupy web admin """
from os.path import join
from flask import render_template, redirect, url_for, request
from admin import app
from admin.database import db_session
from admin.models import Page


@app.route('/')
def index():
    """ Main page """
    pages = Page.query.all()
    return render_template("index.j2", pages=pages)


@app.route('/add', methods=['POST', 'GET'])
def add_page():
    """ add a new page """
    if request.method == 'POST':
        page = Page("test", "test")
        db_session.add(page)
        db_session.commit()
        return redirect(url_for('edit', page_id=page._id))
    return "@todo: Create add page"


@app.route('/edit/<int:page_id>')
def edit_page(page_id):
    """ edit a page """
    page = Page.query.get(page_id)
    return render_template('edit.j2', page=page)


@app.route('/js/<path:path>')
def javascript(path):
    """ Serve up javascript """
    return app.send_static_file(join('js', path))
