#!/usr/bin/env python2
# encoding: utf-8
""" run the wgsiserver """

from werkzeug.contrib.fixers import CGIRootFix
from flup.server.fcgi import WSGIServer
from admin import app

if __name__ == '__main__':
    WSGIServer(CGIRootFix(app)).run()
