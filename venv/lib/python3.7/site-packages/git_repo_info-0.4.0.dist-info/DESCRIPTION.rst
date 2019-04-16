========
Overview
========



Provides access to a local git repository's configuration.

* Free software: MIT license

Installation
============

::

    pip install git-repo-info

Documentation
=============

https://python-git-repo-info.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox


Changelog
=========

0.1.0 (2017-06-29)
------------------

* First release on PyPI.


