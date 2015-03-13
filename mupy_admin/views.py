""" views for mupy web admin """
from os import listdir
from os.path import join

from mongoengine import ValidationError

from flask import render_template, redirect, url_for, request, flash

from flask.ext.admin._compat import itervalues, as_unicode
from flask.ext.admin.actions import action
from flask.ext.admin.base import expose
from flask.ext.admin.contrib.mongoengine import ModelView
from flask.ext.admin.helpers import get_form_data, get_redirect_target

from . import app, admin
from .forms import AddForm
from .models import Page
from .utils import video_id, page_to_context, slugify, _list_time


# admin views
class PageModelView(ModelView):
    """ Custom Mongoengine model view for creating pages from
        youtube links, pdfs, etc. create_view uses customized
        forms based on the page-type template.
    """

    def format_error(self, error):
        """ modify exception messages for prettified flashes """
        if isinstance(error, ValidationError):
            return '. '.join(itervalues(error.to_dict()))
        return as_unicode(error)

    def get_create_form(self):
        """ this will return the proper form based on the selected
            template
        """
        return AddForm

    def create_form(self, obj=None):
        """ instantiate the custom forms based on selected template """
        try:
            templates = listdir(join(app.config['ABSOLUTE_PATH'],
                                app.template_folder, 'posts'))
        except OSError:
            return self.get_form()
        form = self._create_form_class(get_form_data(), obj=obj)
        form.template.choices = zip(templates, templates)
        return form

    def create_model(self, form):
        """ uses selected template and data from the create form to
            add a model to the database.
        """
        try:
            model = self.model()
            template = getattr(form.template, "data", "_youtube.j2")
            model.slug = slugify(form.title.data)
            model.title = form.title.data
            model.body = render_template(join('posts/', template),
                                         video_id=video_id(form.youtube.data),
                                         page=model)
            model.save()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash('Failed to create record. {error}'.
                      format(error=self.format_error(ex)), 'error')
            return False
        else:
            self.after_model_change(form, model, True)
        return True

    def is_action_allowed(self, name):
        """ lets you know if this view can upload """
        if name == 'upload' and not self.can_upload:
            return False

        return super(PageModelView, self).is_action_allowed(name)

    def upload_model(self, obj):
        """ Creates a fake file with cStringIO, then uploads it via FTP """
        from datetime import datetime
        from ftplib import FTP
        from cStringIO import StringIO

        try:
            context = page_to_context(obj)
            filename = obj.slug + '.html'
            outfile = StringIO(render_template('_base.j2', **context))

            ftp = FTP('ftp.alternatorparts.com', 'alternat', 'dubalt493')
            ftp.cwd('httpdocs')
            ftp.storbinary('STOR %s' % filename, outfile)
            ftp.close()
            outfile.close()
            obj.last_upload = datetime.now()
            obj.save()
        except Exception as ex:
            flash('Failed upload page model. {error}'.
                  format(error=self.format_error(ex)), 'error')
            return False
        return True

    @action('upload', 'Upload', 'Are you sure you want to upload?')
    def action_upload(self, ids):
        """ Upload a list of pages """
        try:
            all_ids = [self.object_id_converter(pk) for pk in ids]
            for obj in self.get_query().in_bulk(all_ids).values():
                self.upload_model(obj)

            flash('Pages succesfully uploaded.', 'message')
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash('Failed to upload Pages {error}'.format(error=str(ex)),
                      'error')

    @expose('/upload/', methods=['GET', 'POST'])
    def upload_view(self):
        """ upload the page and return to the list view """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_upload:
            flash('Page upload not allowed', 'error')

        _id = request.args.get('id', None)
        if _id is None:
            flash('Page id not given', 'error')

        model = self.get_one(_id)

        if model is None:
            flash('Page not found', 'error')

        if not self.upload_model(model):
            flash('Failed to upload Page', 'error')
        else:
            flash('Uploaded Page successfully', 'message')

        return redirect(return_url)

    @expose('/preview/', methods=['GET', 'POST'])
    def preview_view(self):
        """ Show the page's remote counterpart """
        return_url = self.get_url('.index_view')

        _id = request.args.get('id', None)
        if _id is None:
            flash('Page id not given', 'error')

        model = self.get_one(_id)

        if model is None:
            flash('Page not found', 'error')
        else:
            return_url = 'http://alternatorparts.com/{url}'.format(
                url=model.slug+'.html')

        return redirect(return_url)

    can_upload = True
    form_excluded_columns = ('last_upload', 'slug')
    column_list = ('title', 'last_upload')
    column_formatters = {
        'last_upload': _list_time
    }
    create_template = 'edit.html'
    edit_template = 'edit.html'
    list_template = 'list.html'

admin.add_view(PageModelView(Page, name='Pages'))

# regular views


@app.route('/')
def index():
    """ Main page, redirect to the admin index.
        @todo: implement a login page
    """
    return redirect(url_for("admin.index"))
