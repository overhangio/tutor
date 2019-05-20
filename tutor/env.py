import codecs
import os
import shutil

import jinja2

from . import exceptions
from . import fmt
from . import utils
from .__about__ import __version__


TEMPLATES_ROOT = os.path.join(os.path.dirname(__file__), "templates")
VERSION_FILENAME = "version"


class Renderer:
    ENVIRONMENT = None

    @classmethod
    def environment(cls):
        if not cls.ENVIRONMENT:
            environment = jinja2.Environment(
                loader=jinja2.FileSystemLoader(TEMPLATES_ROOT),
                undefined=jinja2.StrictUndefined,
            )
            environment.filters["random_string"] = utils.random_string
            environment.filters["common_domain"] = utils.random_string
            environment.filters["reverse_host"] = utils.reverse_host
            environment.globals["TUTOR_VERSION"] = __version__
            cls.ENVIRONMENT = environment

        return cls.ENVIRONMENT

    @classmethod
    def reset(cls):
        cls.ENVIRONMENT = None

    @classmethod
    def render_str(cls, config, text):
        template = cls.environment().from_string(text)
        return cls.__render(template, config)

    @classmethod
    def render_file(cls, config, path):
        template = cls.environment().get_template(path)
        try:
            return cls.__render(template, config)
        except (jinja2.exceptions.TemplateError, exceptions.TutorError):
            fmt.echo_error("Error rendering template " + path)
            raise
        except Exception:
            fmt.echo_error("Unknown error rendering template " + path)
            raise

    @classmethod
    def __render(cls, template, config):
        try:
            return template.render(**config)
        except jinja2.exceptions.UndefinedError as e:
            raise exceptions.TutorError(
                "Missing configuration value: {}".format(e.args[0])
            )


def render_full(root, config):
    """
    Render the full environment, including version information.
    """
    for subdir in ["android", "apps", "k8s", "local", "webui"]:
        render_subdir(subdir, root, config)
    copy_subdir("build", root)
    render_file(config, VERSION_FILENAME)


def render_subdir(subdir, root, config):
    """
    Render the templates located in `subdir` and store them with the same
    hierarchy at `root`.
    """
    for path in walk_templates(subdir):
        dst = pathjoin(root, path)
        rendered = render_file(config, path)
        utils.ensure_file_directory_exists(dst)
        with open(dst, "w") as of:
            of.write(rendered)


def render_file(config, *path):
    """
    Return the rendered contents of a template.
    """
    return Renderer.render_file(config, os.path.join(*path))


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
    return Renderer.render_str(config, text)


def copy_subdir(subdir, root):
    """
    Copy the templates located in `subdir` and store them with the same hierarchy
    at `root`. No rendering is done here.
    """
    for path in walk_templates(subdir):
        src = os.path.join(TEMPLATES_ROOT, path)
        dst = pathjoin(root, path)
        utils.ensure_file_directory_exists(dst)
        shutil.copy(src, dst)


def is_up_to_date(root):
    """
    Check if the currently rendered version is equal to the current tutor version.
    """
    return version(root) == __version__


def version(root):
    """
    Return the current environment version. If the current environment has no version,
    return "0".
    """
    path = pathjoin(root, VERSION_FILENAME)
    if not os.path.exists(path):
        return "0"
    return open(path).read().strip()


def read(*path):
    """
    Read raw content of template located at `path`.
    """
    src = template_path(*path)
    with codecs.open(src, encoding="utf-8") as fi:
        return fi.read()


def walk_templates(subdir):
    """
    Iterate on the template files from `templates/<subdir>`.

    Yield:
        path: template path relative to the template root
    """
    for dirpath, _, filenames in os.walk(template_path(subdir)):
        if not is_part_of_env(dirpath):
            continue
        for filename in filenames:
            path = os.path.join(os.path.relpath(dirpath, TEMPLATES_ROOT), filename)
            if is_part_of_env(path):
                yield path


def is_part_of_env(path):
    """
    Determines whether a file should be rendered or not.
    """
    basename = os.path.basename(path)
    return not (
        basename.startswith(".")
        or basename.endswith(".pyc")
        or basename == "__pycache__"
    )


def template_path(*path):
    """
    Return the template file's absolute path.
    """
    return os.path.join(TEMPLATES_ROOT, *path)


def data_path(root, *path):
    """
    Return the file's absolute path inside the data directory.
    """
    return os.path.join(root_dir(root), "data", *path)


def pathjoin(root, *path):
    """
    Return the file's absolute path inside the environment.
    """
    return os.path.join(base_dir(root), *path)


def base_dir(root):
    """
    Return the environment base directory.
    """
    return os.path.join(root_dir(root), "env")


def root_dir(root):
    """
    Return the project root directory.
    """
    return os.path.abspath(root)
