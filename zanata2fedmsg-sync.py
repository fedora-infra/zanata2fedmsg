#!/usr/bin/env python


import zanata2fedmsg

import requests

import logging
logging.basicConfig(level='DEBUG')

log = logging.getLogger()

s = requests.session()

zanata = 'https://fedora.zanata.org'
headers = dict(
    accept='application/json',
)

def list_zanata_projects():
    response = s.get(zanata + '/rest/projects', headers=headers)
    projects = response.json()
    for entry in projects:
        yield entry['id']
    raise NotImplementedError("That's only the first page of results.. how do I get the second?")


def update_or_install_webhook(name):
    secret = zanata2fedmsg.compute_per_project_secret(name)
    url = 'https://apps.fedoraproject.org/zanata2fedmsg/webhook/%s' % name
    raise NotImplementedError


if __name__ == '__main__':
    zanata_projects = list_zanata_projects()

    for project in zanata_projects:
        update_or_install_webhook(project)
