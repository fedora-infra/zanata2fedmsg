Try it out
----------

Run the server::

    $ ZANATA2FEDMSG_CONFIG=./dev.ini python zanata2fedmsg.py

Generate example urls for zanata::

    $ ZANATA2FEDMSG_CONFIG=$(pwd)/dev.ini python utility/zanata2fedmsg-webhook-generator.py asknot-ng
    URL for asknot-ng is
    https://apps.fedoraproject.org/zanata2fedmsg/webhook/5c605f0f4dd27a5cd81b053bedd06ec153f2272f82c8a49b0842eab7f3c73141

