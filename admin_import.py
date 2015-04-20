#!/usr/bin/env python
# encoding: utf-8
import sys
import os
import os.path as op
from mu import Engine, Page, PAGES_DIR, OUTPUT_DIR
from mupy_admin.models import Pages, Products, MetaData, ImportProducts
from mupy_admin.utils import slugify

UPDATE_OPERATORS = ('set', 'unset', 'inc', 'dec', 'pop', 'push',
                    'push_all', 'pull', 'pull_all', 'add_to_set',
                    'set_on_insert', 'min', 'max')


def update_addops(**update):
    def generator(**update):
        for key, value in update.items():
            parts = key.split('__')
            if parts[0] not in UPDATE_OPERATORS:
                parts.insert(0, 'set')
            yield '__'.join(parts), value
    return dict(generator(**update))


def titleify(slug):
    return ' '.join('-'.split(slug)).title()


def prepare_weight(major, minor):
    return int(major) + (float(minor) / 16)


def prepare_url(url):
    from urlparse import urlparse
    from os.path import splitext, basename
    prod_url, prod_ext = splitext(basename(urlparse(url).path))
    return prod_url


def prepare_products(row):
    variations = row['Variations']

    if variations != '':
        variations = variations.split('| ')
        variations_header = variations.pop(0)
        variations = variations[0].split('; ')
        variations.pop()
        print variations_header, variations
    else:
        variations_header = None
        variations = None

    if row['ProductUrl'] == '':
        variation = True
    else:
        variation = False

    return dict(
        name=row['Name'],
        short_desc=row['ShortDescription'],
        long_desc=row['LongDescription'],
        part_num=row['PartNumber'],
        price=row['CustomerPrice'],
        cost=row['StoreCost'],
        weight=prepare_weight(
            row['WeightMajor'],
            row['WeightMinor']
        ),
        manufacturer_name=row['ManufacturerName'],
        manufacturer_partn=row['ManufacturerPartNumber'],
        url=prepare_url(row['ProductUrl']),
        variation=variation,
        variations=variations,
        variations_header=variations_header,
        meta_data=MetaData(
            title=row['MetaTitle'],
            keywords=row['MetaKeywords'],
            description=row['MetaDescription']
        )
    )


class AdminEngine(Engine):
    def run(self):
        for line in os.listdir(self.indir):
            inpath = op.join(self.indir, line)
            if op.isfile(inpath):
                print inpath
                page = Page.from_file(inpath)
                slug = op.splitext(line)[0]
                title = page.context.get('title', "Default Title")
                if title == '':
                    title = titleify(slug)
                body = page.context.get('body', "Blank Body")
                keywords = page.context.get('keywords', '')
                description = page.context.get('description', '')
                update = update_addops(
                    title=title,
                    body=body,
                    keywords=keywords,
                    description=description
                )
                Pages.objects(slug=slug).update_one(
                    upsert=True,
                    **update
                )
            else:
                continue


def import_pages():
    engine = AdminEngine(PAGES_DIR, OUTPUT_DIR)
    engine.run()


def import_products():
    import csv
    with open('products.csv') as prods_file:
        prods_reader = csv.DictReader(prods_file)
        for row in prods_reader:
            update = prepare_products(row)
            update = update_addops(**update)
            ImportProducts.objects(product_id=row['ProductID']).update_one(
                upsert=True,
                **update
            )


def products_from_import():
    for import_prod in ImportProducts.objects.timeout(False).all():
        update = dict(
            name=import_prod.name,
            part_num=import_prod.part_num,
            price=import_prod.price,
            cost=import_prod.cost,
            weight=import_prod.weight,
            manufacturer_partn=import_prod.manufacturer_partn,
            variation=import_prod.variation,
            variations=import_prod.variations,
        )
        if import_prod.variation:
            parent_id = import_prod.variations[0]
            parent = ImportProducts.objects(product_id=parent_id).first()
            update.update(
                dict(
                    short_desc=parent.short_desc,
                    long_desc=parent.long_desc,
                    url=parent.url,
                    meta_data=parent.meta_data,
                )
            )
        else:
            update.update(
                dict(
                    short_desc=import_prod.short_desc,
                    long_desc=import_prod.long_desc,
                    url=import_prod.url,
                    meta_data=import_prod.meta_data,
                )
            )
        update = update_addops(**update)
        Products.objects(product_id=import_prod.product_id).update_one(
            upsert=True,
            **update
        )


def prepare_variations():
    products = ImportProducts.objects.timeout(False).all()
    for product in products:
        if product.variation is True:
            prod_name = product.name.split('| ')[0]
            parent_id = ImportProducts.objects(
                name=prod_name).first().product_id
            product.variations = [str(parent_id)]
            product.save()
        elif product.variations_header is not None:
            print product.product_id
            variants = ImportProducts.objects(
                variations__contains=str(product.product_id))
            variant_ids = [str(v.product_id) for v in variants]
            product.variations = variant_ids
            print 'Product has variants', variant_ids
            product.save()
        else:
            continue


def main():
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'products':
            import_products()
        if sys.argv[1] == 'pages':
            import_pages()
        if sys.argv[1] == 'prep':
            prepare_variations()
        if sys.argv[1] == 'imports':
            products_from_import()
    else:
        print sys.argv

if __name__ == '__main__':
    main()
