#!/usr/bin/env python
# encoding: utf-8

import os
import os.path as op
import sys
import re

import jinja2
import yaml
from markdown import markdown
from typogrify.templatetags import jinja_filters

FIND_MD = re.compile('^.*\.md$')
DEFAULT_TEMPLATE = '_base.j2'
TEMPLATE_DIR = './templates'
PAGES_DIR = './pages'
OUTPUT_DIR = './output'

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
            page.fulltext = pagefile.read().decode('utf-8')
            page.context = yaml.load(page.fulltext)

        page.prepare_context()
        page.template = page.context.pop('template', DEFAULT_TEMPLATE)
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
                page = Page.from_file(inpath)
                with open(outpath, 'w') as outfile:
                    outfile.write(page.render().encode('utf-8', 'ignore'))

if __name__ == '__main__':
    engine = Engine(PAGES_DIR, OUTPUT_DIR)
    engine.run()
