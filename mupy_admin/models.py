""" database models for mupy web admin """
from . import db
from .fields import PriceField


class MetaData(db.EmbeddedDocument):
    title = db.StringField()
    keywords = db.StringField()
    desc = db.StringField()


class ImportProducts(db.DynamicDocument):
    """ Collection for imported products """
    product_id = db.LongField(unique=True)
    variation = db.BooleanField()
    variations = db.ListField(db.StringField())
    name = db.StringField()
    meta = {
        'allow_inheritance': False,
        'indexes': ['product_id'],
        'ordering': ['product_id']
    }


class Products(db.DynamicDocument):
    """ products for pages """
    name = db.StringField(required=True)
    product_id = db.IntField(unique=True)
    short_desc = db.StringField(max_length=255)
    long_desc = db.StringField()
    part_num = db.StringField(max_length=75)
    price = PriceField(currency='USD')
    cost = PriceField(currency='USD')
    weight = db.DecimalField()
    manufacturer_partn = db.StringField(max_length=75)
    manufacturer_name = db.StringField(max_length=75)
    url = db.StringField()
    meta_data = db.EmbeddedDocumentField(MetaData)
    variation = db.BooleanField(default=False)
    variations = db.ListField(db.IntField())
    meta = {
        'allow_inheritance': True,
        'indexes': ['name', 'url', 'product_id'],
        'ordering': ['price', 'name']
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


class ProductSets(db.EmbeddedDocument):
    """ Product set for pages, includes intro, products, etc """
    title = db.StringField(max_length=75)
    products = db.ListField(db.ReferenceField(Products))
    meta = {
        'allow_inheritance': False,
        'ordering': ['sort_order']
    }


class Pages(db.DynamicDocument):
    """ basic mupy page model """

    page_num = db.IntField()
    slug = db.StringField(required=True, max_length=255, unique=True)
    title = db.StringField(required=True, max_length=255)
    keywords = db.StringField()
    description = db.StringField()
    body = db.StringField(required=True)
    last_upload = db.DateTimeField()
    product_sets = db.ListField(db.EmbeddedDocumentField(ProductSets))
    meta = {
        'allow_inheritance': True,
        'indexes': ['title', 'slug', 'keywords'],
        'ordering': ['page_num', 'title']
    }

    def __unicode__(self):
        return self.title
