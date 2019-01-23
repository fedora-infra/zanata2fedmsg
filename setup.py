#!/usr/bin/env python
from setuptools import setup

setup(
    name='zanata2fedmsg',
    description='Bridge Zanata to Fedora Messaging',
    version='0.2',
    author='Ralph Bean',
    author_email='rbean@redhat.com',
    license='GPLv2+',
    url='https://github.com/fedora-infra/zanata2fedmsg',
    py_modules=['zanata2fedmsg'],
    packages=[],
    install_requires=['fedora_messaging', 'flask'],
    scripts=[
        'utility/zanata2fedmsg-webhook-generator.py',
    ],
)
