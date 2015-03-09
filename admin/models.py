""" database models for mupy web admin """
from admin import db


class Page(db.DynamicDocument):
    """ basic mupy page model """

    slug = db.StringField(required=True, max_length=255, unique=True)
    title = db.StringField(required=True, max_length=255)
    keywords = db.StringField()
    description = db.StringField()
    body = db.StringField(required=True)

    def __unicode__(self):
        return self.title

    meta = {
        'allow_inheritance': True,
        'indexes': ['title', 'slug'],
        'ordering': ['title']
    }
