PositionStatements
==================

PositionStatements is a bot based on `Pywikibot <https://www.mediawiki.org/wiki/Manual:Pywikibot>`. It works in a similar way to `QuickStatements <https://tools.wmflabs.org/wikidata-todo/quick_statements.php>` but works around a problem we ran into when trying to add multiple P39 statements. See `this issue <https://github.com/everypolitician/everypolitician/issues/615>` for the background.

Installation
------------

Before installing you'll need to make sure you've got a working version of Python 3 and `Pipenv <https://github.com/kennethreitz/pipenv>`

::

    $ git clone https://github.com/everypolitician/position_statements.git
    $ cd position_statements
    $ pipenv install
    $ cp user-config.py-example user-config.py

Then open `user-config.py` and add the username for the bot you want to use. For full documentation see `Manual:Pywikibot/user-config.py <https://www.mediawiki.org/wiki/Manual:Pywikibot/user-config.py#ExampleBot_on_Wikidata>`.

Usage
-----

Run the `position_statements.py` script, passing it the path to a TSV file of `QuickStatements <https://tools.wmflabs.org/wikidata-todo/quick_statements.php>`.

::

    $ pipenv run python position_statements.py example_statements.tsv
