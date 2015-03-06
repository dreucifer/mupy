""" views for mupy web admin """
from os import listdir
from os.path import join, dirname
from flask import render_template, redirect, url_for, request, flash, abort, send_from_directory
from sqlalchemy.exc import IntegrityError
from admin import app
from admin.database import db_session
from admin.forms import AddForm, EditForm
from admin.models import Page
from admin.utils import video_id, page_to_context, slugify


@app.route('/')
def index():
    """ Main page """
    pages = Page.query.all()
    return render_template("index.j2", pages=pages)


@app.route('/add', methods=['POST', 'GET'])
def add():
    """ add a new page """
    try:
        templates = listdir(join(app.config['ABSOLUTE_PATH'],
            app.template_folder, 'posts')) 
    except OSError:
        abort(500)
    add_form = AddForm(request.form)
    add_form.template.choices = zip(templates, templates)
    if request.method == 'POST' and add_form.validate():
        template = getattr(add_form.template, "data", "_youtube.j2")
        page = Page(slug=slugify(add_form.title.data),
                title=add_form.title.data)
        page.body = render_template(join('posts/', template),
                video_id=video_id(add_form.youtube.data),
                page=page)
        try:
            db_session.add(page)
            db_session.commit()
        except IntegrityError, e:
            flash('Could not add page: %s' % e.message)
        else:
            return redirect(url_for('edit', slug=page.slug))
    return render_template('add.j2', form=add_form)


@app.route('/edit/<slug>', methods=['POST', 'GET'])
def edit(slug):
    """ edit a page """
    page = Page.query.filter_by(slug=slug).first()
    if page is None:
        abort(404)
    form = EditForm(request.form, page)
    if request.method == 'POST':
        form.populate_obj(page)
        db_session.commit()
    return render_template('edit.j2', page=page, form=form)


@app.route('/delete', methods=['POST'])
def delete():
    page_id = request.values.get("page_id")
    if request.method == 'POST' and page_id is not None:
        page = Page.query.get(page_id)
        db_session.delete(page)
        db_session.commit()
    return redirect(url_for('index'))


@app.route('/preview/<slug>')
def preview(slug):
    """ preview a page """
    page = Page.query.filter_by(slug=slug).first()
    if page is None:
        abort(404)
    context = page_to_context(page)
    return render_template('preview.j2', **context)


@app.route('/generate/<slug>')
def generate(slug):
    page = Page.query.filter_by(slug=slug).first() 
    if page is None:
        abort(404)
    context = page_to_context(page)
    directory = app.config['OUTPUT_FOLDER']
    filename = page.slug + '.html'

    from os import fsync
    from ftplib import FTP
    ftp = FTP('ftp.alternatorparts.com', 'alternat', 'dubalt493')
    ftp.cwd('httpdocs')
    with open(join(directory, filename), "w") as outfile:
        outfile.write(render_template('_base.j2', **context))
        outfile.flush()
        fsync(outfile.fileno())
    with open(join(directory, filename), 'r') as readfile:
        ftp.storbinary('STOR %s' % filename, readfile)
        ftp.close()
    return redirect('http://alternatorparts.com/%s' % filename)
