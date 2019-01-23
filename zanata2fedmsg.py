""" zanata2fedmsg.py

This is a small Flask app designed to receive the POST webhook callbacks fired
by fedora.zanata.org.  Upon receiving a POST, this webapp will try to verify
that it actually came from zanata and then republish the payload to our own
Fedora Messaging bus.

Author:     Ralph Bean <rbean@redhat.com>
License:    GPLv2+
"""

import base64
import hmac
import hashlib
import json
import re

import flask
from fedora_messaging.api import Message, publish
from fedora_messaging.exceptions import PublishReturned, ConnectionException

import logging
log = logging.getLogger()

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


def compute_per_project_secret(name):
    salt = app.config['WEBHOOK_SALT']
    return hmac.new(salt, name, hashlib.sha256).hexdigest()


@app.route('/')
def index():
    return "Source:  https://github.com/fedora-infra/zanata2fedmsg"


def camel2dot(camel):
    """ Convert CamelCaseText to dot.separated.text. """
    regexp = r'([A-Z][a-z0-9]+|[a-z0-9]+|[A-Z0-9]+)'
    return '.'.join([s.lower() for s in re.findall(regexp, camel)])


@app.route('/webhook/<url_project>', methods=['POST'])
def webhook(url_project):

    # First, verify that the hashed url sent to us is the one that we provided
    # to zanata in the first place.

    header_hash = flask.request.headers.get('X-Zanata-Webhook', None)
    if not header_hash:
        error = 'No X-Zanata-Webhook header found on the request.'
        return error, 403

    payload = json.loads(flask.request.data)

    name = payload['project']
    if name != url_project:
        error = "projects don't match:  %r != %r" % (url_project, name)
        return error, 400

    url = flask.request.url
    url = url.replace('http:', 'https:')
    content = flask.request.data.encode('utf-8') + url.encode('utf-8')
    secret = compute_per_project_secret(name)

    log.debug("per-project secret for %r is %r" % (name, secret))
    log.debug("Verifying content %r" % content)

    # This is insane.
    # http://docs.zanata.org/en/release/user-guide/projects/project-settings/#webhooks
    local_hash = base64.b64encode(
        hmac.new(
            secret,
            base64.b64encode(
                hmac.new(secret, content, hashlib.sha1).hexdigest()
            ),
            hashlib.sha1
        ).hexdigest()
    )
    log.debug("Comparing %r with %r" % (header_hash, local_hash))

    if header_hash != local_hash:
        error = "%s is not valid for %s" % (header_hash, name)
        return error, 403

    # Having verified the message, we're all set.  Republish it on our bus.
    topic = camel2dot(payload['eventType'].split('.')[-1])
    try:
        msg = Message(
            topic="zanata.{}.v1".format(topic),
            body=payload,
        )
        publish(msg)
    except PublishReturned as e:
        log.warning(
            "Fedora Messaging broker rejected message %s: %s",
            msg.id, e
        )
    except ConnectionException as e:
        log.warning("Error sending message %s: %s", msg.id, e)
    return "Everything is 200 OK"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
