#!/usr/bin/env python
from setuptools import setup

setup(
    name='zanata2fedmsg',
    description='zanata2fedmsg bridges zanata to fedmsg',
    version='0.1',
    author='Ralph Bean',
    author_email='rbean@redhat.com',
    license='GPLv3+',
    url='https://github.com/fedora-infra/zanata2fedmsg',
    py_modules=['zanata2fedmsg'],
    packages=[],
    install_requires=['fedmsg', 'flask'],
    scripts=[
        'utility/zanata2fedmsg-webhook-generator.py',
    ],
)
