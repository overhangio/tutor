import io
import os
import sys
from typing import Any, Dict, List

import docutils
import docutils.parsers.rst

# -- Project information -----------------------------------------------------

project = "Tutor"
copyright = ""
author = "Overhang.io"

# The short X.Y version
version = ""
# The full version, including alpha/beta/rc tags
release = ""


# -- General configuration ---------------------------------------------------
extensions = []
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
language = None
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = None

# Autodocumentation of modules
extensions.append("sphinx.ext.autodoc")
autodoc_typehints = "description"

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
html_logo = "./img/tutor-logo.png"
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
    exec(f.read(), about)
rst_prolog = """
.. |tutor_version| replace:: {}
""".format(
    about["__version__"],
)


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
            """
<iframe width="560" height="315"
    src="https://www.youtube-nocookie.com/embed/{video_id}"
    frameborder="0"
    allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>
</iframe>""".format(
                video_id=video_id
            ),
            format="html",
        )
    ]


# Tutor's own extension
sys.path.append(os.path.join(os.path.dirname(__file__), "_ext"))
extensions.append("tutordocs")


setattr(youtube, "content", True)
docutils.parsers.rst.directives.register_directive("youtube", youtube)  # type: ignore
