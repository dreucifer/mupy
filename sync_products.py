#!/usr/bin/env python
# encoding: utf-8
from nscommerceapi.products import NsProducts
from mupy_admin.models import Products


def sync_model(obj, product_app):
    """ Creates a fake file with cStringIO, then uploads it via FTP """
    from decimal import Decimal
    product = None
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
            product, 'FullDescription', obj.long_desc).encode('utf-8')
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
    else:
        return False
    return True


def main():
    product_app = NsProducts()
    for product in Products.objects.timeout(False).order_by('product_id').all():
        print product.product_id, product.name
        if sync_model(product, product_app) is False:
            break

if __name__ == '__main__':
    main()
