.. birchrest documentation master file, created by
   sphinx-quickstart on Thu Oct 10 08:31:56 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Birchrest Documentation
=======================

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   modules

# Include your README file for the front page content
.. include:: ../README.md
   :parser: myst_parser.sphinx_

# Automatically generate summaries for all modules and submodules
Modules and Submodules
======================

.. autosummary::
   :toctree: _autosummary
   :recursive:

   birchrest
   birchrest.app
   birchrest.decorators
   birchrest.exceptions
   birchrest.http
   birchrest.middlewares
   birchrest.routes
   birchrest.types
   birchrest.unittest
   birchrest.utils
