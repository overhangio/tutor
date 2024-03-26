from __future__ import annotations

import io
import os
import sys
from typing import Any, Dict, List

import docutils
import docutils.parsers.rst

# -- Project information -----------------------------------------------------

project = "Tutor"
copyright = ""  # pylint: disable=redefined-builtin
author = "Overhang.IO"

# The short X.Y version
version = ""
# The full version, including alpha/beta/rc tags
release = ""


# -- General configuration ---------------------------------------------------
extensions = []
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = None

# Autodocumentation of modules
extensions.append("sphinx.ext.autodoc")
autodoc_typehints = "description"
# For the life of me I can't get the docs to compile in nitpicky mode without these
# ignore statements. You are most welcome to try and remove them.
# To make matters worse, some ignores are only required for some versions of Python,
# from 3.8 to 3.10...
nitpick_ignore = [
    # Sphinx does not handle ParamSpec arguments
    ("py:class", "T.args"),
    ("py:class", "T.kwargs"),
    ("py:class", "T2.args"),
    ("py:class", "T2.kwargs"),
    # Sphinx doesn't know about the following classes
    ("py:class", "click.Command"),
    ("py:class", "t.Any"),
    ("py:class", "t.Callable"),
    ("py:class", "t.Iterator"),
    ("py:class", "t.Optional"),
    # python 3.10
    ("py:class", "NoneType"),
    ("py:class", "click.core.Command"),
    # Python 3.12
    ("py:class", "FilterCallbackFunc"),
]
# Resolve type aliases here
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_type_aliases
autodoc_type_aliases: dict[str, str] = {
    # python 3.10
    "T": "tutor.core.hooks.actions.T",
    "T2": "tutor.core.hooks.filters.T2",
    # # python 3.12
    "L": "tutor.core.hooks.filters.L",
    "FilterCallbackFunc": "tutor.core.hooks.filters.FilterCallbackFunc",
    # https://stackoverflow.com/questions/73223417/type-aliases-in-type-hints-are-not-preserved
    # https://github.com/sphinx-doc/sphinx/issues/10455
    # https://github.com/sphinx-doc/sphinx/issues/10785
    # https://github.com/emdgroup/baybe/pull/67
    "Action": "tutor.core.hooks.actions.Action",
    "Filter": "tutor.core.hooks.filters.Filter",
}


# -- Sphinx-Click configuration
# https://sphinx-click.readthedocs.io/
extensions.append("sphinx_click")
# This is to avoid the addition of the local username to the docs
os.environ["HOME"] = "~"
# Make sure that sphinx-click can find the tutor module
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "logo_only": True,
    "style_nav_header_background": "#EFEFEF",
}
html_context = {
    "display_github": True,
    "github_user": "overhangio",
    "github_repo": "tutor",
    "github_version": "master",
    "conf_py_path": "/docs/",
}
html_static_path = ["img"]

# Custom settings
html_logo = "https://overhang.io/static/img/tutor-logo.svg"
html_favicon = "./img/favicon.png"
html_show_sourcelink = False
html_display_github = True
html_show_sphinx = False
html_github_user = "overhangio"
html_github_repo = "tutor"
# Images do not link to themselves
html_scaled_image_link = False
html_show_copyright = False

# Custom variables
here = os.path.abspath(os.path.dirname(__file__))
about: Dict[str, str] = {}
with io.open(
    os.path.join(here, "..", "tutor", "__about__.py"), "rt", encoding="utf-8"
) as f:
    # pylint: disable=exec-used
    exec(f.read(), about)
rst_prolog = f"""
.. |tutor_version| replace:: {about["__version__"]}
"""


# Custom directives
def youtube(
    _name: Any,
    _args: Any,
    _options: Any,
    content: List[str],
    _lineno: Any,
    _contentOffset: Any,
    _blockText: Any,
    _state: Any,
    _stateMachine: Any,
) -> Any:
    """Restructured text extension for inserting youtube embedded videos"""
    if not content:
        return []
    video_id = content[0]
    return [
        docutils.nodes.raw(
            "",
            f"""
<iframe width="560" height="315"
    src="https://www.youtube-nocookie.com/embed/{video_id}"
    frameborder="0"
    allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>
</iframe>""",
            format="html",
        )
    ]


# Tutor's own extension
sys.path.append(os.path.join(os.path.dirname(__file__), "_ext"))
extensions.append("tutordocs")


setattr(youtube, "content", True)
docutils.parsers.rst.directives.register_directive("youtube", youtube)  # type: ignore
