""" views for mupy web admin """
from os.path import join

from mongoengine import ValidationError
from mongoengine.errors import NotUniqueError

from flask import render_template, redirect, url_for, request, flash

from flask.ext.admin._compat import itervalues, as_unicode
from flask.ext.admin.actions import action
from flask.ext.admin.base import expose
from flask.ext.admin.contrib.mongoengine import ModelView
from flask.ext.admin.contrib.mongoengine.form import get_form
from flask.ext.admin.contrib.mongoengine.filters import FilterInList, FilterEqual
from flask.ext.admin.form import FormOpts, rules
from flask.ext.admin.helpers import get_form_data, get_redirect_target
from flask.ext.admin.model.helpers import get_mdict_item_or_list

from flask.ext.babel import gettext

from . import app, admin
from .forms import AddForm, AddYoutubeForm, ProductsModelConverter
from .models import Pages, Products, Shelves, ImportProducts
from .utils import video_id, page_to_context, slugify
from .formatters import _list_time, _list_prices
from .filters import FilterLikeInsensitive


# admin views
class ImportProductsModelView(ModelView):
    column_filters = (
        'name',
        'product_id',
        'variation',
        FilterInList(ImportProducts.variations, 'variations')
    )


class ProductsModelView(ModelView):
    """ MongoEngine model view for managing products (with prices)
    """

    def format_error(self, error):
        """ modify exception messages for prettified flashes """
        if isinstance(error, ValidationError):
            return '. '.join(itervalues(error.to_dict()))
        return as_unicode(error)

    def scaffold_form(self):
        form_class = get_form(self.model,
                              self.model_form_converter(self),
                              base_class=self.form_base_class,
                              only=self.form_columns,
                              exclude=self.form_excluded_columns,
                              field_args=self.form_args,
                              extra_fields=self.form_extra_fields)

        return form_class

    def sync_model(self, obj):
        """ Creates a fake file with cStringIO, then uploads it via FTP """
        from nscommerceapi.products import NsProducts
        from decimal import Decimal
        try:
            product = None
            product_app = NsProducts()
            client = product_app.client

            filterlist = client.factory.create('FilterType')
            filterlist.Field = 'ProductId'
            filterlist.Operator.value = 'Equal'
            filterlist.ValueList = long(obj.product_id)

            response = client.service.ReadProduct(
                DetailSize="Large",
                FilterList=filterlist
            )

            if response is not None:
                if response.Status == "Success" and \
                        hasattr(response, 'ProductList'):
                    product = response.ProductList[0]
                    try:
                        delattr(product, "PageUrl")
                    except:
                        print "Page has no PageUrl"
                else:
                    flash(
                        'Failed to look up model {name}'.format(name=obj.name),
                        'error'
                    )

                if product is not None:
                    price_obj = getattr(product, 'Price', None)
                    if price_obj is not None:
                        if hasattr(price_obj, 'BasePrice'):
                            price = price_obj.BasePrice.value
                        else:
                            price = obj.price.net
                        if hasattr(price_obj, 'Cost'):
                            cost = price_obj.Cost.value
                        else:
                            cost = obj.cost.net

                    obj.name = product.Name.encode('utf-8')
                    obj.short_desc = getattr(
                        product, 'Description', obj.short_desc).encode('utf-8')
                    obj.long_desc = getattr(
                        product,
                        'FullDescription',
                        obj.long_desc
                    ).encode('utf-8')
                    obj.part_num = getattr(
                        product, 'PartNumber', obj.part_num).encode('utf-8')
                    obj.manufacturer_partn = getattr(
                        product,
                        'ManufacturerPartNumber',
                        obj.manufacturer_partn
                    ).encode('utf-8')
                    obj.price = Decimal(price)
                    obj.cost = Decimal(cost)
                obj.save()

        except UnicodeEncodeError as ex:
            flash('Failed sync page model. {error}'.format(
                error=ex), 'error')
        finally:
            flash('Failed sync page model. {error}'.format(
                error=ex), 'error')
            return False
        return True

    @action('sync', 'Sync', 'Are you sure you want to sync?')
    def action_sync(self, ids):
        """ Sync a list of products """
        try:
            all_ids = [self.object_id_converter(pk) for pk in ids]
            for obj in self.get_query().in_bulk(all_ids).values():
                self.sync_model(obj)

        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash('Failed to sync Products {error}'.format(error=str(ex)),
                      'error')

    model_form_converter = ProductsModelConverter
    column_list = ('product_id', 'name', 'short_desc', 'price')
    column_filters = ('name', 'part_num', 'manufacturer_partn', 'product_id')
    column_formatters = {
        'price': _list_prices
    }
    edit_template = 'edit_product.html'
    form_edit_rules = [
        rules.FieldSet(
            (
                'name',
                'part_num',
                'manufacturer_partn',
                'manufacturer_name',
            ),
            'Basic Product Info'
        ),
        'product_id',
        'variations',
        'variation',
        'url',
        'meta_data',
        rules.FieldSet(
            (
                'price',
                'cost',
                'weight',
            ),
            'Pricing & Weight'
        ),
        rules.FieldSet(
            (
                'short_desc',
                'long_desc',
            ),
            'Description'
        ),
    ]


class PagesModelView(ModelView):
    """ Custom Mongoengine model view for creating pages from
        youtube links, pdfs, etc. create_view uses customized
        forms based on the page-type template.
    """

    def format_error(self, error):
        """ modify exception messages for prettified flashes """
        if isinstance(error, ValidationError):
            return '. '.join(itervalues(error.to_dict()))
        return as_unicode(error)

    def render_body(self, form, model):
        if self.template == '_youtube.j2':
            return render_template(join('posts/', self.template),
                                   video_id=video_id(form.youtube.data),
                                   page=model)

        return render_template('posts/_base.j2', page=model)

    def is_action_allowed(self, name):
        """ lets you know if this view can upload """
        if name == 'upload' and not self.can_upload:
            return False

        return super(PagesModelView, self).is_action_allowed(name)

    def get_create_form(self):
        """ this will return the proper form based on the selected
            template
        """
        if self.template == '_youtube.j2':
            return AddYoutubeForm

        return AddForm

    def create_form(self, obj=None):
        """ instantiate the custom forms based on selected template """
        self._create_form_class = self.get_create_form()
        form = self._create_form_class(get_form_data(), obj=obj)
        return form

    def create_model(self, form):
        """ uses selected template and data from the create form to
            add a model to the database.
        """
        try:
            model = self.model()
            model.slug = slugify(form.title.data)
            model.title = form.title.data
            model.body = self.render_body(form, model)
            model.save()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash('Failed to create record. {error}'.
                      format(error=self.format_error(ex)), 'error')
            return False, None
        else:
            self.after_model_change(form, model, True)
        return True, model

    def upload_model(self, model):
        """ Creates a fake file with cStringIO, then uploads it via FTP """
        from datetime import datetime
        from ftplib import FTP
        from cStringIO import StringIO

        try:
            context = page_to_context(model)
            filename = model.slug + '.html'
            outfile = StringIO(render_template('_base.j2', **context))

            ftp = FTP('ftp.alternatorparts.com', 'alternat', 'dubalt493')
            ftp.cwd('httpdocs')
            ftp.storbinary('STOR %s' % filename, outfile)
            ftp.close()
            outfile.close()
            model.last_upload = datetime.now()
            model.save()
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

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_create:
            return redirect(return_url)

        self.template = request.args.get('template', None)
        form = self.create_form()

        if self.validate_form(form):
            try:
                ret_bool, obj = self.create_model(form)
            except NotUniqueError:
                flash('Record creation failed.', 'error')
                return redirect(return_url)

            if ret_bool:
                if '_add_another' in request.form:
                    flash('Record was successfully created.')
                    return redirect(return_url)
                elif obj is not None:
                    return_url = self.get_url(
                        '.edit_view',
                        id=obj.pk,
                        url=self.get_url('.index_view')
                    )
                    flash('Record was successfully created.')
                    return redirect(return_url)
                else:
                    flash('Record creation failed.')
                    return redirect(return_url)

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_create_rules)

        return self.render(self.create_template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_edit:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            return redirect(return_url)

        form = self.edit_form(obj=model)
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_create_rules, form=form)

        if self.validate_form(form):
            if self.update_model(form, model):
                flash(gettext('Record was successfully saved.'))
                if '_save_upload' in request.form:
                    if self.upload_model(model) is True:
                        flash(gettext('Record was successfully uploaded.'))
                    else:
                        flash(gettext('Record could not be uploaded.'))
                    return redirect(request.url)
                if '_continue_editing' in request.form:
                    return redirect(request.url)
                else:
                    return redirect(return_url)

        if request.method == 'GET':
            self.on_form_prefill(form, id)

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_edit_rules)

        return self.render(self.edit_template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)

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
    form_excluded_columns = ('last_upload')
    column_filters = (
        FilterLikeInsensitive(Pages.title, 'Title'),
        FilterLikeInsensitive(Pages.slug, 'URL'),
        FilterLikeInsensitive(Pages.keywords, 'Keywords'),
        FilterEqual(Pages.page_num, 'PageID'),
    )
    column_list = ('page_num', 'title', 'last_upload')
    column_formatters = {
        'last_upload': _list_time
    }
    template = None
    edit_template = 'edit_page.html'
    list_template = 'list.html'


admin.add_view(PagesModelView(Pages, name='Pages'))
admin.add_view(ProductsModelView(Products, name='Products'))
admin.add_view(ModelView(Shelves, name='Shelves'))
admin.add_view(ImportProductsModelView(ImportProducts, name='Imports'))


# regular views
@app.route('/')
def index():
    """ Main page, redirect to the admin index.
        @todo: implement a login page
    """
    return redirect(url_for("admin.index"))


# config.js
@app.route('/config.js')
def config_js():
    """ Return the CKeditor config.js file
    """
    return app.send_static_file('config.js')
