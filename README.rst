PositionStatements
==================

PositionStatements is a bot based on `Pywikibot <https://www.mediawiki.org/wiki/Manual:Pywikibot>`_. It works in a similar way to `QuickStatements <https://tools.wmflabs.org/wikidata-todo/quick_statements.php>`_ but works around a problem we ran into when trying to add multiple P39 statements. See `this issue <https://github.com/everypolitician/everypolitician/issues/615>`_ for the background.

Installation
------------

Before installing you'll need to make sure you've got a working version of Python 3 and `Pipenv <https://github.com/kennethreitz/pipenv>`_

::

    $ git clone https://github.com/everypolitician/position_statements.git
    $ cd position_statements
    $ pipenv install
    $ cp user-config.py-example user-config.py

Then open `user-config.py` and add the username for the bot you want to use. For full documentation see `Manual:Pywikibot/user-config.py <https://www.mediawiki.org/wiki/Manual:Pywikibot/user-config.py#ExampleBot_on_Wikidata>`_.

Usage
-----

Run the `position_statements.py` script, passing it the path to a TSV file of `QuickStatements <https://tools.wmflabs.org/wikidata-todo/quick_statements.php>`_.

::

    $ pipenv run python position_statements.py example_statements.tsv

If you want to add user attribution in the edit summary then you can specify a user name as an additional argument on the command line.

::

    $ pipenv run python position_statements.py example_statements.tsv 'Chris Mytton'
