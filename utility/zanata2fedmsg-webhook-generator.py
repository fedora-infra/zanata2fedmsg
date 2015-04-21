#!/usr/bin/env python

import hmac
import hashlib
import sys

import flask

app = flask.Flask(__name__)
app.config.from_envvar('ZANATA2FEDMSG_CONFIG')

salt = app.config['WEBHOOK_SALT']

name = sys.argv[-1]
valid_secret = hmac.new(salt, name, hashlib.sha256).hexdigest()
print "URL for %s is" % name
print "https://apps.fedoraproject.org/zanata2fedmsg/webhook/%s" % valid_secret
