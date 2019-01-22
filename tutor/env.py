import codecs
import os
import shutil

import jinja2

from . import exceptions
from . import utils


TEMPLATES_ROOT = os.path.join(os.path.dirname(__file__), "templates")

def render_target(root, config, target):
    """
    Render the templates located in `target` and store them with the same
    hierarchy at `root`.
    """
    for src, dst in walk_templates(root, target):
        if is_part_of_env(src):
            with codecs.open(src, encoding='utf-8') as fi:
                substituted = render_str(fi.read(), config)
            with open(dst, "w") as of:
                of.write(substituted)

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
            rendered[key] = render_str(value, config)
        else:
            rendered[key] = value
    for k, v in rendered.items():
        config[k] = v
    pass

def render_str(text, config):
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
            RAND8=utils.random_string(8),
            RAND24=utils.random_string(24),
            **config
        )
    except jinja2.exceptions.UndefinedError as e:
        raise exceptions.TutorError("Missing configuration value: {}".format(e.args[0]))

def copy_target(root, target):
    """
    Copy the templates located in `path` and store them with the same hierarchy
    at `root`.
    """
    for src, dst in walk_templates(root, target):
        if is_part_of_env(src):
            shutil.copy(src, dst)

def is_part_of_env(path):
    return not os.path.basename(path).startswith(".")

def read(*path):
    """
    Read template content located at `path`.
    """
    src = os.path.join(TEMPLATES_ROOT, *path)
    with codecs.open(src, encoding='utf-8') as fi:
        return fi.read()

def walk_templates(root, target):
    """
    Iterate on the template files from `templates/target`.

    Yield:
        src: template path
        dst: destination path inside root
    """
    target_root = os.path.join(TEMPLATES_ROOT, target)
    for dirpath, _, filenames in os.walk(os.path.join(TEMPLATES_ROOT, target)):
        dst_dir = pathjoin(
            root, target,
            os.path.relpath(dirpath, target_root)
        )
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for filename in filenames:
            src = os.path.join(dirpath, filename)
            dst = os.path.join(dst_dir, filename)
            yield src, dst

def data_path(root, *path):
    return os.path.join(os.path.abspath(root), "data", *path)

def pathjoin(root, target, *path):
    return os.path.join(root, "env", target, *path)
