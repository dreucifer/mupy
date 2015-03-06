""" database models for mupy web admin """
from sqlalchemy import Column, Integer, String, Text
from admin.database import Base


class Page(Base):
    """ basic mupy page model """
    __tablename__ = "pages"

    _id = Column(Integer, primary_key=True)
    slug = Column(String, unique=True)
    title = Column(String, unique=True)
    keywords = Column(String)
    description = Column(Text)
    body = Column(Text)

    def __init__(self, slug=None, title=None):
        self.slug = slug
        self.title = title

    def __repr__(self):
        return "<Page(slug='%s', title='%s')>" % (
            self.slug, self.title)
