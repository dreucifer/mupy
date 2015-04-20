#!/usr/bin/env python
# encoding: utf-8

import csv
from decimal import Decimal
from mupy_admin.models import Products


def check_costs():
    outfile = open('price-differences.csv', 'w+')
    pricewriter = csv.DictWriter(
        outfile,
        ['Query Name', 'Match Name', 'Cost Diff', 'Cost'])
    pricewriter.writeheader()

    with open('price-list-wai.csv', 'r') as pricefile:
        pricereader = csv.DictReader(pricefile)
        for row in pricereader:
            product = Products.objects(
                manufacturer_name__contains=row['Item'].replace('-', '')
            ).first()
            if product is not None:
                cost_diff = product.cost.net - Decimal(row['Sales Price'])

                print "{name:25} {query:15} {cost_diff} {new_cost}".format(
                    cost_diff=cost_diff,
                    name=product.name[:25],
                    query=row['Item'],
                    new_cost=row['Sales Price']
                )
                pricewriter.writerow({
                    'Query Name': row['Item'],
                    'Match Name': product.name.encode('ascii', 'ignore'),
                    'Cost Diff': cost_diff,
                    'Cost': Decimal(row['Sales Price'])
                })

    outfile.close()


def check_profits():
    profit_outfile = open('profits.csv', 'w+')
    profitwriter = csv.DictWriter(
        profit_outfile,
        ['ID', 'Name', 'Cost', 'Price', 'Profit', 'Margin']
    )
    profitwriter.writeheader()
    for product in Products.objects.timeout(False).all():
        profit = product.price.net - product.cost.net

        if product.cost.net > 0:
            margin = product.price.net / product.cost.net
        else:
            margin = 0

        print "{name:25} {price:8} {cost:8} {profit:8}".format(
            cost=product.cost.net,
            name=product.name[:25],
            price=product.price.net,
            profit=profit
        )

        profitwriter.writerow({
            'ID': product.product_id,
            'Name': product.name.encode('utf-8'),
            'Price': product.price.net,
            'Cost': product.cost.net,
            'Profit': profit,
            'Margin': margin
        })

    profit_outfile.close()


def main():
    check_profits()


if __name__ == '__main__':
    main()
