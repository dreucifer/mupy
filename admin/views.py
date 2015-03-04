""" views for mupy web admin """
from os.path import join
from flask import render_template, redirect, url_for, request
from admin import app
from admin.database import db_session
from admin.forms import AddForm, EditForm
from admin.models import Page
from admin.utils import video_id


@app.route('/')
def index():
    """ Main page """
    pages = Page.query.all()
    return render_template("index.j2", pages=pages)


@app.route('/add', methods=['POST', 'GET'])
def add_page():
    """ add a new page """
    add_form = AddForm(request.form)
    if request.method == 'POST':
        page = Page(slug=add_form.slug.data, title=add_form.title.data)
        page.body = render_template('_youtube.j2',
                video_id=video_id(add_form.youtube.data))
        db_session.add(page)
        db_session.commit()
        return redirect(url_for('edit_page', page_id=page._id))
    return render_template('add.j2', form=add_form)


@app.route('/edit/<int:page_id>', methods=['POST', 'GET'])
def edit_page(page_id):
    """ edit a page """
    page = Page.query.get(page_id)
    form = EditForm(request.form, page)
    if request.method == 'POST':
        form.populate_obj(page)
        db_session.commit()
    return render_template('edit.j2', page=page, form=form)


@app.route('/js/<path:path>')
def javascript(path):
    """ Serve up javascript """
    return app.send_static_file(join('js', path))
