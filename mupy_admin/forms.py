""" forms for the mupy web admin """
from flask.ext.mongoengine.wtf import orm
from flask.ext.admin.form import BaseForm
from flask.ext.admin.contrib.mongoengine.form import CustomModelConverter
from wtforms import TextField, TextAreaField, validators
from prices import Price


class PriceField(TextField):
    def _value(self):
        if self.data is not None:
            if isinstance(self.data, Price):
                return unicode("${net} {currency}".format(
                    net=self.data.net,
                    currency=self.data.currency))
            else:
                return unicode(self.data)
        else:
            return unicode(0)

    def process_formdata(self, valuelist):
        import re
        from decimal import InvalidOperation
        price_currency = r'\$([0-9]+\.?[0-9]+)\s([A-Z]+)$'
        if valuelist:
            m = re.search(price_currency, valuelist[0])
            if m is not None:
                args = dict(zip(('net', 'currency'), m.group(1, 2)))
            try:
                self.data = Price(**args)
            except (ValueError, InvalidOperation):
                self.data = None
                raise ValueError(self.gettext('Not a valid price value'))


class ProductsModelConverter(CustomModelConverter):
    @orm.converts('PriceField')
    def conv_PriceField(self, model, field, kwargs):
        return PriceField(**kwargs)


class AddForm(BaseForm):
    title = TextField('Page Title', [validators.Length(min=5, max=255)])


class AddYoutubeForm(AddForm):
    youtube = TextField('YouTube URL', [validators.Required()])


class EditForm(BaseForm):
    slug = TextField('New Page URL', [validators.Length(min=5, max=255)])
    title = TextField('Page Title', [validators.Length(min=5, max=255)])
    body = TextAreaField('Page Body', [validators.Required()])
    keywords = TextField('Keywords')
    description = TextAreaField('Description')
