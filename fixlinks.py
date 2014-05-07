#!/usr/bin/env python
# encoding: utf-8
import os
import os.path as op
import re
import sys

import yaml
import bs4
import urlparse
from urllib import unquote
from mu import slugify

FIXDIR = './output/'
LOCAL = re.compile(r'^[w]*\.?alternatorparts.com')
HTTP_LINK = re.compile(r'^.*[:].*$')
ROOT_LINK = re.compile(r'^[/]$')
BOOKMARK = re.compile(r'^#.*$')

def filter_pages(fixdir=FIXDIR):
    for path in os.listdir(fixdir):
        inpath = op.join(fixdir, path)
        if op.isfile(inpath) and path.endswith('yml'):
            print inpath
            with open(inpath, 'r') as readfile:
                page_data = yaml.load(readfile.read())
                try:
                    soup = bs4.BeautifulSoup(page_data['body'])
                except KeyError:
                    continue
            links = soup.find_all('a')
            filter_links(links)
            page = str(soup).decode('utf-8', 'ignore')
            page_data['body'] = page
            with open(inpath, 'w') as outfile:
                outfile.write(yaml.dump(page_data, default_flow_style=False))

def filter_output(fixdir=FIXDIR):
    """List files in FIXDIR and process them for link fixing"""
    for path in os.listdir(fixdir):
        inpath = op.join(fixdir, path)
        if op.isfile(inpath) and path.endswith('html'):
            print inpath
            with open(inpath, 'r') as readfile:
                soup = bs4.BeautifulSoup(readfile)
            links = soup.find_all('a')
            filter_links(links)
            page = str(soup).decode('utf-8', 'ignore')
            with open(inpath, 'w') as writefile:
                writefile.write(page.encode('utf-8', 'ignore'))

def filter_links(links):
    for link in links:
        try:
            href = link['href']
        except KeyError:
            continue
        scheme, netloc, path, query, fragment = urlparse.urlsplit(unquote(href))
        if path == '' or path == '/':
            continue
        if path.endswith(('.html', '.htm')):
            path = path.split('/')[-1]
            if LOCAL.match(netloc) or netloc == '':
                link['href'] = slugify(op.splitext(path)[0]) + '.html'

def main():
    with sys.stdin as stdin:
        soup = bs4.BeautifulSoup(stdin.read())
    links = soup.find_all('a')
    filter_links(links)
    page = str(soup)
    print page


if __name__ == '__main__':
    filter_pages('./pages/')
