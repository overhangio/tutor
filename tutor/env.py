import codecs
import os
import shutil

import jinja2

from . import exceptions
from . import utils
from .__about__ import __version__


TEMPLATES_ROOT = os.path.join(os.path.dirname(__file__), "templates")
VERSION_FILENAME = "version"


def render_full(root, config):
    """
    Render the full environment, including version information.
    """
    for target in ["android", "apps", "k8s", "local", "webui"]:
        render_target(root, config, target)
    copy_target(root, "build")
    with open(pathjoin(root, VERSION_FILENAME), "w") as f:
        f.write(__version__)


def render_target(root, config, target):
    """
    Render the templates located in `target` and store them with the same
    hierarchy at `root`.
    """
    for src, dst in walk_templates(root, target):
        rendered = render_file(config, src)
        with open(dst, "w") as of:
            of.write(rendered)


def render_file(config, path):
    with codecs.open(path, encoding="utf-8") as fi:
        try:
            return render_str(config, fi.read())
        except jinja2.exceptions.TemplateError:
            print("Error rendering template", path)
            raise
        except Exception:
            print("Unknown error rendering template", path)
            raise


def render_dict(config):
    """
    Render the values from the dict. This is useful for rendering the default
    values from config.yml.

    Args:
        config (dict)
    """
    rendered = {}
    for key, value in config.items():
        if isinstance(value, str):
            rendered[key] = render_str(config, value)
        else:
            rendered[key] = value
    for k, v in rendered.items():
        config[k] = v


def render_str(config, text):
    """
    Args:
        text (str)
        config (dict)

    Return:
        substituted (str)
    """
    template = jinja2.Template(text, undefined=jinja2.StrictUndefined)
    try:
        return template.render(
            RAND8=utils.random_string(8), RAND24=utils.random_string(24), **config
        )
    except jinja2.exceptions.UndefinedError as e:
        raise exceptions.TutorError("Missing configuration value: {}".format(e.args[0]))


def copy_target(root, target):
    """
    Copy the templates located in `path` and store them with the same hierarchy
    at `root`.
    """
    for src, dst in walk_templates(root, target):
        shutil.copy(src, dst)


def is_up_to_date(root):
    return version(root) == __version__


def version(root):
    """
    Return the current environment version.
    """
    path = pathjoin(root, VERSION_FILENAME)
    if not os.path.exists(path):
        return "0"
    return open(path).read().strip()


def read(*path):
    """
    Read template content located at `path`.
    """
    src = template_path(*path)
    with codecs.open(src, encoding="utf-8") as fi:
        return fi.read()


def walk_templates(root, target):
    """
    Iterate on the template files from `templates/target`.

    Yield:
        src: template path
        dst: destination path inside root
    """
    target_root = template_path(target)
    for dirpath, _, filenames in os.walk(target_root):
        if not is_part_of_env(dirpath):
            continue
        dst_dir = pathjoin(root, target, os.path.relpath(dirpath, target_root))
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for filename in filenames:
            src = os.path.join(dirpath, filename)
            dst = os.path.join(dst_dir, filename)
            if is_part_of_env(src):
                yield src, dst


def is_part_of_env(path):
    basename = os.path.basename(path)
    return not (
        basename.startswith(".")
        or basename.endswith(".pyc")
        or basename == "__pycache__"
    )


def template_path(*path):
    return os.path.join(TEMPLATES_ROOT, *path)


def data_path(root, *path):
    return os.path.join(os.path.abspath(root), "data", *path)


def pathjoin(root, target, *path):
    return os.path.join(base_dir(root), target, *path)


def base_dir(root):
    return os.path.join(root, "env")
