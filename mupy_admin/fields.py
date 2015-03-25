""" Custom Fields for MongoEngine documents """
from . import db
from prices import Price


class PriceField(db.DecimalField):
    """ price field (mostly stolen from mirumee's django-prices)
        Saves the price in the database as a decimal
    """

    def __init__(self, currency=None, **kwargs):
        self.currency = currency
        super(PriceField, self).__init__(**kwargs)

    def to_python(self, value):
        if isinstance(value, Price):
            if value.currency is None:
                value.currency = self.currency
            if value.currency != self.currency:
                self.error('Invalid currency: %r (expected %r)' % (
                    value.currency, self.currency))
            return value
        value = super(PriceField, self).to_python(value)
        if value is None:
            return value
        return Price(value, currency=self.currency)

    def validate(self, value):
        if value is None:
            super(PriceField, self).validate(value)

        if not isinstance(value, Price):
            value = Price(value)
            if value is None:
                self.error('PriceField could not convert value')

    def lookup_member(self, member_name):
        return None

    def to_mongo(self, value, **kwargs):
        value = self.to_python(value)
        if value is not None:
            value = value.net
        return float(value)

    def prepare_query_value(self, op, value):
        return self.to_mongo(value)
