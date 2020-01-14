import codecs
from copy import deepcopy
import os
import shutil

import jinja2
import pkg_resources

from . import exceptions
from . import fmt
from . import plugins
from . import utils
from .__about__ import __version__


TEMPLATES_ROOT = pkg_resources.resource_filename("tutor", "templates")
VERSION_FILENAME = "version"


class Renderer:
    ENVIRONMENT = None
    ENVIRONMENT_CONFIG = None

    @classmethod
    def environment(cls, config):
        def patch(name, separator="\n", suffix=""):
            return cls.__render_patch(config, name, separator=separator, suffix=suffix)

        if cls.ENVIRONMENT_CONFIG != config:
            # Load template roots
            template_roots = [TEMPLATES_ROOT]
            for _, plugin_template_root in plugins.iter_template_roots(config):
                template_roots.append(plugin_template_root)

            # Create environment
            environment = jinja2.Environment(
                loader=jinja2.FileSystemLoader(template_roots),
                undefined=jinja2.StrictUndefined,
            )
            environment.filters["random_string"] = utils.random_string
            environment.filters["common_domain"] = utils.common_domain
            environment.filters["list_if"] = utils.list_if
            environment.filters["reverse_host"] = utils.reverse_host
            environment.filters["walk_templates"] = walk_templates
            environment.globals["patch"] = patch
            environment.globals["TUTOR_VERSION"] = __version__

            # Update environment singleton
            cls.ENVIRONMENT_CONFIG = deepcopy(config)
            cls.ENVIRONMENT = environment

        return cls.ENVIRONMENT

    @classmethod
    def reset(cls):
        cls.ENVIRONMENT = None
        cls.ENVIRONMENT_CONFIG = None

    @classmethod
    def render_str(cls, config, text):
        template = cls.environment(config).from_string(text)
        return cls.__render(config, template)

    @classmethod
    def render_file(cls, config, path):
        try:
            template = cls.environment(config).get_template(path)
        except Exception:
            fmt.echo_error("Error loading template " + path)
            raise
        try:
            return cls.__render(config, template)
        except (jinja2.exceptions.TemplateError, exceptions.TutorError):
            fmt.echo_error("Error rendering template " + path)
            raise
        except Exception:
            fmt.echo_error("Unknown error rendering template " + path)
            raise

    @classmethod
    def __render(cls, config, template):
        try:
            return template.render(**config)
        except jinja2.exceptions.UndefinedError as e:
            raise exceptions.TutorError(
                "Missing configuration value: {}".format(e.args[0])
            )

    @classmethod
    def __render_patch(cls, config, name, separator="\n", suffix=""):
        """
        Render calls to {{ patch("...") }} in environment templates from plugin patches.
        """
        patches = []
        for plugin, patch in plugins.iter_patches(config, name):
            patch_template = cls.environment(config).from_string(patch)
            try:
                patches.append(patch_template.render(**config))
            except jinja2.exceptions.UndefinedError as e:
                raise exceptions.TutorError(
                    "Missing configuration value: {} in patch '{}' from plugin {}".format(
                        e.args[0], name, plugin
                    )
                )
        rendered = separator.join(patches)
        if rendered:
            rendered += suffix
        return rendered


def save(root, config):
    render_full(root, config)
    fmt.echo_info("Environment generated in {}".format(base_dir(root)))


def render_full(root, config):
    """
    Render the full environment, including version information.
    """
    for subdir in ["android", "apps", "build", "dev", "k8s", "local", "webui"]:
        save_subdir(subdir, root, config)
    for plugin, path in plugins.iter_template_roots(config):
        save_plugin_templates(plugin, path, root, config)
    save_file(VERSION_FILENAME, root, config)
    save_file("kustomization.yml", root, config)


def save_plugin_templates(plugin, plugin_path, root, config):
    """
    Save plugin templates to plugins/<plugin name>/*.
    Only the "apps" and "build" subfolders are rendered.
    """
    for subdir in ["apps", "build"]:
        path = os.path.join(plugin_path, plugin, subdir)
        for src in walk_templates(path, root=plugin_path):
            dst = pathjoin(root, "plugins", src)
            rendered = render_file(config, src)
            write_to(rendered, dst)


def save_subdir(subdir, root, config):
    """
    Render the templates located in `subdir` and store them with the same
    hierarchy at `root`.
    """
    for path in walk_templates(subdir):
        save_file(path, root, config)


def save_file(path, root, config):
    """
    Render the template located in `path` and store it with the same hierarchy at `root`.
    """
    dst = pathjoin(root, path)
    rendered = render_file(config, path)
    write_to(rendered, dst)


def write_to(content, path):
    utils.ensure_file_directory_exists(path)
    with open(path, "w") as of:
        of.write(content)


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


def render_unknown(config, value):
    if isinstance(value, str):
        return render_str(config, value)
    return value


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


def check_is_up_to_date(root):
    if not is_up_to_date(root):
        message = (
            "The current environment stored at {} is not up-to-date: it is at "
            "v{} while the 'tutor' binary is at v{}. You should upgrade "
            "the environment by running:\n"
            "\n"
            "    tutor config save"
        )
        fmt.echo_alert(message.format(base_dir(root), version(root), __version__))


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


def walk_templates(subdir, root=TEMPLATES_ROOT):
    """
    Iterate on the template files from `templates/<subdir>`.

    Yield:
        path: template path relative to the template root
    """
    for dirpath, _, filenames in os.walk(template_path(subdir)):
        if not is_part_of_env(dirpath):
            continue
        for filename in filenames:
            path = os.path.join(os.path.relpath(dirpath, root), filename)
            if is_part_of_env(path):
                yield path


def is_part_of_env(path):
    """
    Determines whether a file should be rendered or not.
    """
    basename = os.path.basename(path)
    is_excluded = False
    is_excluded = is_excluded or basename.startswith(".") or basename.endswith(".pyc")
    is_excluded = is_excluded or basename == "__pycache__" or basename == "partials"
    return not is_excluded


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
