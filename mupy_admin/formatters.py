""" Various formatters for list views etc. Basically anything that needs a
    nice __repr__
"""


def _list_time(view, context, model, name):
    """ formatter for DatetimeField in list view """
    if not model.last_upload:
        return unicode('Never')

    return unicode(model.last_upload.strftime('%D %T'))


def _list_prices(view, context, model, name):
    """ formatter for PriceField in list view """
    return unicode(''.join([
        '$', str(model.price.net),
        ' ', model.price.currency]))
