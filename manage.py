#!/usr/bin/env python
# encoding: utf-8

import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from flask.ext.script import Manager, Server
from mupy_admin import app

manager = Manager(app)

manager.add_command("runserver", Server(
    use_debugger=True,
    use_reloader=True,
    host='127.0.0.1')
)

if __name__ == '__main__':
    manager.run()
