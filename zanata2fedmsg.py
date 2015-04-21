""" zanata2fedmsg.py

This is a small Flask app designed to receive the POST webhook callbacks fired
by fedora.zanata.org.  Upon receiving a POST, this webapp will try to verify
that it actually came from zanata and then republish the payload to our own
fedmsg bus.

Author:     Ralph Bean <rbean@redhat.com>
License:    GPLv3+
"""

import hmac
import hashlib
import json
import os
import re

import fedmsg
import flask

app = flask.Flask(__name__)
app.config.from_envvar('ZANATA2FEDMSG_CONFIG')

## Here's an example payload from zanata itself
#body = {
#    "project": "webhooks-dummy",
#    "version": "0.1",
#    "docId": "foo.txt",
#    "locale": "af",
#    "milestone": "100% Translated",
#    "eventType": "org.zanata.event.DocumentMilestoneEvent",
#}


def camel2dot(camel):
    """ Convert CamelCaseText to dot.separated.text. """
    regexp = r'([A-Z][a-z0-9]+|[a-z0-9]+|[A-Z0-9]+)'
    return '.'.join([s.lower() for s in re.findall(regexp, camel)])


@app.route('/webhook/<provided_secret>', methods=['POST'])
def webhook(provided_secret):

    # First, verify that the hashed url sent to us is the one that we provided
    # to zanata in the first place.
    salt = app.config['WEBHOOK_SALT']
    payload = json.loads(flask.request.body)
    name = payload['project']
    valid_secret = hmac.new(salt, name, hashlib.sha256).hexdigest()

    if provided_secret != valid_secret:
        error = "%s is not valid for %s" % (provided_secret, name)
        return error, 403

    # XXX - Note that the validation mechanism we used above is not really
    # secure. An attacker could eavesdrop on the request and get the url and
    # then perform a replay attack (since the provided_secret will be the same
    # every time for each project).  It would be better to use a shared salt
    # and then sign each message uniquely, but we'll have to wait until zanata
    # supports something like that.  This will do in the mean time.
    # See https://bugzilla.redhat.com/show_bug.cgi?id=1213630

    # Having verified the message, we're all set.  Republish it on our bus.
    topic = camel2dot(payload['eventType'].split('.')[-1])
    fedmsg.publish(
        modname='zanata',
        topic=topic,
        msg=payload,
    )
    return "Everything is 200 OK"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
