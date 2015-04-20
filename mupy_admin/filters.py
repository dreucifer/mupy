from flask.ext.admin.contrib.mongoengine.filters import BaseMongoEngineFilter
from flask.ext.admin.babel import lazy_gettext

from typogrify.filters import smartypants

from . import app


@app.template_filter('smartypants')
def smartypants_filter(s):
    return smartypants(s)


class FilterLikeInsensitive(BaseMongoEngineFilter):
    def apply(self, query, value):
        flt = {'%s__%s' % (self.column.name, 'icontains'): value}
        return query.filter(**flt)

    def operation(self):
        return lazy_gettext('icontains')
