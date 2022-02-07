"""
This module is heavily inspired by Django's djangodocs.py:
https://github.com/django/django/blob/main/docs/_ext/djangodocs.py
"""
from sphinx.application import Sphinx


def setup(app: Sphinx) -> None:
    # https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx.application.Sphinx.add_crossref_type
    app.add_crossref_type(
        directivename="patch",
        rolename="patch",
        indextemplate="pair: %s; patch",
    )
