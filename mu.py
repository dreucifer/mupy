#!/usr/bin/env python
# coding: utf-8

import os
from filecmp import dircmp, cmpfiles
from markdown import markdown
from typogrify.templatetags import jinja_filters
from urllib import unquote
import argparse
import bs4
import codecs
import jinja2
import os
import os.path as op
import re
import sys
import urlparse
import yaml

BOOKMARK = re.compile(r'^#.*$')
DEFAULT_TEMPLATE = '_base.j2'
FIND_MD = re.compile('^.*\.md$')
FIXDIR = './output/'
HTTP_LINK = re.compile(r'^.*[:].*$')
LOCAL = re.compile(r'^[w]*\.?alternatorparts.com')
OUTPUT_DIR = 'output/'
PAGES_DIR = 'pages/'
TEMP_DIR = 'tmp/'
ROOT_LINK = re.compile(r'^[/]$')
TEMPLATE_DIR = 'templates/'

# snippet provided by Armin Ronacher http://flask.pocoo.org/snippets/5/
from unicodedata import normalize

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim='-'):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        if word:
            result.append(word)
    return delim.join(result)

def filter_buffer():
    with sys.stdin as stdin:
        soup = bs4.BeautifulSoup(stdin.read())
    links = soup.find_all('a')
    filter_links(links)
    page = str(soup)
    print page

def filter_pages(fixdir='pages'):
    for path in os.listdir(fixdir):
        inpath = op.join(fixdir, path)
        if op.isfile(inpath) and path.endswith('yml'):
            print inpath
            with open(inpath, 'r') as readfile:
                page_data = yaml.load(readfile.read())
                try:
                    soup = bs4.BeautifulSoup(page_data['body'])
                except KeyError, err:
                    print err
                    continue
            links = soup.find_all('a')
            filter_links(links)
            page = str(soup).decode('utf-8', 'ignore')
            page_data['body'] = page
            with open(inpath, 'w') as outfile:
                outfile.write(yaml.dump(page_data, default_flow_style=False))

def filter_output(fixdir='output'):
    """List files in FIXDIR and process them for link fixing"""
    for path in os.listdir(fixdir):
        inpath = op.join(fixdir, path)
        if op.isfile(inpath) and path.endswith('html'):
            print inpath
            with open(inpath, 'r') as readfile:
                soup = bs4.BeautifulSoup(readfile)
            links = soup.find_all('a')
            filter_links(links)
            page = soup.decode('utf-8', 'ignore')
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

def unpack_pages(fixdir='pages/'):
    for path in os.listdir(fixdir):
        inpath = op.join(fixdir, path)
        if op.isfile(inpath) and path.endswith('yml'):
            print inpath
            unpack_file(inpath)

def pack_pages(fixdir='pages/'):
    for path in os.listdir(fixdir):
        inpath = op.join(fixdir, path)
        if op.isfile(inpath) and path.endswith('yml'):
            print inpath
            pack_file(inpath)

def pack_file(filepath):
    print 'test'
    with open(filepath, 'r') as readfile:
        page_obj = yaml.load(readfile.read())
    with open(filepath, 'w') as writefile:
        writefile.write(yaml.dump(page_obj, default_flow_style=False))

def tab_buffer(bufin):
    return '\n'.join('    ' + line for line in bufin.split('\n'))

def unpack_file(filepath):
    fmt = """\
{body_tag}: |
{body}
"""
    with open(filepath, 'r') as readfile:
        page = yaml.load(readfile.read().decode('utf-8', 'ignore'))
    if 'body.md' in page:
        body_tag = 'body.md'
        body = tab_buffer(page.pop('body.md', '').encode('utf-8', 'ignore'))
    else:
        try:
            body_tag = 'body'
            body = tab_buffer(page.pop('body', '').encode('utf-8', 'ignore'))
        except KeyError, err:
            print err
            return None
    with open(filepath, 'w') as writefile:
        writefile.write(yaml.dump(page, default_flow_style=False))
        writefile.write(fmt.format(body_tag=body_tag, body=body))

def unpack_buffer():
    with sys.stdin as stdin:
        print stdin.read().decode('string-escape')
def find_tagstring(taglist):
    for tag in taglist:
        if tag:
            return tag['content']
    return ''


def decompose_if_exists(tag):
    if tag:
        tag.decompose()


class Page(object):
    tmpl_env = None

    def __init__(self):
        self.filename = None
        self.fulltext = None
        self.context = None
        self.template = DEFAULT_TEMPLATE
        self.tmpl_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
        jinja_filters.register(self.tmpl_env)

    @classmethod
    def from_file(cls, filepath):
        page = cls()
        page.filename = op.basename(filepath)

        with open(filepath, 'r') as pagefile:
            page.fulltext = pagefile.read().decode('utf-8', 'ignore')
            try:
                page.context = yaml.load(page.fulltext)
            except yaml.parser.ParserError, err:
                print page.filename, err
                exit(1)

        page.template = page.context.pop('template', DEFAULT_TEMPLATE)
        page.prepare_context()
        return page

    def render(self):
        template = self.tmpl_env.get_template(self.template)
        return template.render(**self.context)

    def prepare_context(self):
        context = self.context
        for key, value in context.items():
            if FIND_MD.match(key):
                try:
                    self.context.pop(key)
                except KeyError:
                    print "This shouldn't happen"
                    continue
                self.context[key[:-3]] = markdown(value, extensions=['extra'])

class Engine(object):
    def __init__(self, indir, outdir):
        self.indir = op.join(os.getcwd(), indir)
        self.outdir = op.join(os.getcwd(), outdir)

    def run(self):
        for line in os.listdir(self.indir):
            inpath = op.join(self.indir, line)
            outpath = op.join(self.outdir, op.splitext(line)[0]+'.html')
            if op.isfile(inpath):
                print inpath
                page = Page.from_file(inpath)
                with open(outpath, 'w') as outfile:
                    outfile.write(page.render().encode('utf-8', 'ignore'))


class HTMLPage(Page):
    def __init__(self):
        self.filename = None
        self.fulltext = None
        self.soup = None
        self.context = dict()

    @classmethod
    def from_file(cls, filepath):
        page = cls()
        page.filename = op.basename(filepath)

        with open(filepath, 'r') as pagefile:
            page.fulltext = pagefile.read()
            page.soup = bs4.BeautifulSoup(page.fulltext)

        page.prepare_context()
        return page

    def prepare_context(self):
        title, keywords, description, body = '', '', '', ''
        try:
            print self.filename
            title = self.soup.title.string.encode('utf-8')
            if not title:
                title = ''
            keywords = find_tagstring(
                    [self.soup.find('meta', {'name': 'keywords'}),
                    self.soup.find('meta', {'name': 'Keywords'})])
            description = find_tagstring(
                    [self.soup.find('meta', {'name': 'description'}),
                    self.soup.find('meta', {'name': 'Description'})])
            decompose_if_exists(self.soup.find(id='header'))
            decompose_if_exists(self.soup.find(id='footer'))
            self.soup.head.decompose()
            self.soup.html.unwrap()
            self.soup.body.unwrap()
            body = self.soup.encode('ascii', 'ignore')
            body = '\n'.join(
                    ['    '+line for line in str(body).split('\n')]
                    ).encode('ascii', 'ignore')

        except AttributeError, err:
            print err
        self.context = """\
title: "{title}"
keywords: "{keywords}"
description: "{description}"
body: |
{body}
""".format(title=' '.join(title.strip('\n').split()),
        keywords=keywords.strip('\n'),
        description=description.strip('\n'),
        body=body)

class Importer(Engine):
    def run(self):
        for line in os.listdir(self.indir):
            inpath = op.join(self.indir, line)
            outpath = op.join(self.outdir, slugify(op.splitext(line)[0])+'.yml')
            if op.isfile(inpath):
                page = HTMLPage.from_file(inpath)
                with open(outpath, 'w') as outfile:
                    outfile.write(page.context)

def import_pages():
    engine = Importer('import', PAGES_DIR)
    engine.run()

def compare_directories(dcmp):
    return cmpfiles(dcmp.left, dcmp.right, dcmp.common_files, True)

def diff_output():
    dcmp = dircmp("output", "tmp")
    vimdiff = "vimdiff -f %s %s"
    same_files, diff_files, funny_files = compare_directories(dcmp)
    for filename in diff_files:
        print filename
        #os.system(vimdiff % (TEMP_DIR+filename, OUTPUT_DIR+filename))

def mupy():
    engine = Engine(PAGES_DIR, OUTPUT_DIR)
    engine.run()

def render_page(page_name):
    inpath = op.join(PAGES_DIR, page_name+'.yml')
    outpath = op.join(OUTPUT_DIR, page_name+'.html')
    if op.isfile(inpath):
        page = Page.from_file(inpath)
        with open(outpath, 'w') as outfile:
            outfile.write(page.render().encode('utf-8', 'ignore'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='some helpers and management functions for mupy')
    parser.add_argument('action', metavar='ACTION', type=str, nargs="?",
            help='What are you going to do?', default=mupy)
    parser.add_argument('-t', dest='target', metavar='TARGET', type=str, nargs=1,
            help='And Where?')
    args = parser.parse_args()
    if args.target:
        print args.target[0]
        try:
            locals()[args.action](args.target[0])
        except KeyError, err:
            print err
    elif args.action != mupy:
        try:
            locals()[args.action]()
        except KeyError, err:
            print err
    else:
        args.action()
