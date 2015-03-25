""" database models for mupy web admin """
from . import db
from .fields import PriceField


class MetaData(db.EmbeddedDocument):
    title = db.StringField(max_length=75)
    keywords = db.StringField(max_length=255)
    desc = db.StringField(max_length=500)


class Products(db.DynamicDocument):
    """ products for pages """
    name = db.StringField(max_length=75, required=True, unique=True)
    short_desc = db.StringField(max_length=255)
    long_desc = db.StringField()
    part_num = db.StringField(max_length=75)
    price = PriceField(currency='USD')
    cost = PriceField(currency='USD')
    weight = db.DecimalField()
    manufacturer_partn = db.StringField(max_length=75)
    manufacturer_name = db.StringField(max_length=75)
    url = db.StringField(max_length=75)
    meta_data = db.EmbeddedDocumentField(MetaData)
    meta = {
        'allow_inheritance': True,
        'indexes': ['name', 'url'],
        'ordering': ['name']
    }

    def __unicode__(self):
        return unicode(self.name)


class ShelfBin(db.EmbeddedDocument):
    """ Shelf bin location model for inventory management """
    sort_order = db.IntField(default=0)
    name = db.StringField()
    product = db.ReferenceField(Products)


class Shelves(db.DynamicDocument):
    """ Shelf model for inventory management """
    name = db.StringField(required=True)
    bins = db.ListField(db.EmbeddedDocumentField(ShelfBin))


class ProductSet(db.EmbeddedDocument):
    """ Product set for pages, includes intro, products, etc """
    title = db.StringField(max_length=75)
    products = db.ListField(db.ReferenceField(Products))


class Pages(db.DynamicDocument):
    """ basic mupy page model """

    slug = db.StringField(required=True, max_length=255, unique=True)
    title = db.StringField(required=True, max_length=255)
    keywords = db.StringField()
    description = db.StringField()
    body = db.StringField(required=True)
    last_upload = db.DateTimeField()
    products = db.EmbeddedDocumentField(ProductSet)
    meta = {
        'allow_inheritance': True,
        'indexes': ['title', 'slug'],
        'ordering': ['title']
    }

    def __unicode__(self):
        return self.title
