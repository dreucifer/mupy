#!/usr/bin/env python
# encoding: utf-8
import os
import os.path as op
from mu import Engine, Page, PAGES_DIR, OUTPUT_DIR
from mupy_admin.models import Pages

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


def main():
    engine = AdminEngine(PAGES_DIR, OUTPUT_DIR)
    engine.run()

if __name__ == '__main__':
    main()
