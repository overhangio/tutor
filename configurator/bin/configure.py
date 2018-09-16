#! /usr/bin/env python3
# coding: utf8
import argparse
import codecs
import json
import os
import random
import string
import sys

from collections import OrderedDict

import jinja2


class Configurator:

    def __init__(self, **default_overrides):
        """
        Default values are read, in decreasing order of priority, from:
        - SETTING_<name> environment variable
        - Existing config file (in `default_overrides`)
        - Value passed to add()
        """
        self.__values = OrderedDict()
        self.__default_values = default_overrides
        try:
            self.__input = raw_input
        except NameError:
            self.__input = input

    def as_dict(self):
        return self.__values

    def mute(self):
        self.__input = None

    def add(self, name, question="", default=""):
        default = self.get_default_value(name, default)
        message = question + " (default: \"{}\"): ".format(default) if question else None
        value = self.ask(message, default)
        self.set(name, value)

        return self

    def add_bool(self, name, question="", default=False):
        self.add(name, question=question, default=default)
        value = self.get(name)
        if value in [1, '1']:
            return self.set(name, True)
        if value in [0, '0', '']:
            return self.set(name, False)
        if value in [True, False]:
            return self
        return self.set(name, bool(value))

    def get_default_value(self, name, default):
        setting_name = 'SETTING_' + name.upper()
        if os.environ.get(setting_name):
            return os.environ[setting_name]

        if name in self.__default_values:
            return self.__default_values[name]

        return default

    def ask(self, message, default):
        if self.__input and message:
            return self.__input(message) or default
        return default

    def get(self, name):
        return self.__values.get(name)

    def set(self, name, value):
        self.__values[name] = value
        return self


def main():
    parser = argparse.ArgumentParser("Config file generator for Open edX")
    parser.add_argument('-c', '--config', default=os.path.join("/", "openedx", "config", "config.json"),
                        help="Load default values from this file. Config values will be saved there.")
    subparsers = parser.add_subparsers()

    parser_interactive = subparsers.add_parser('interactive')
    parser_interactive.add_argument('-s', '--silent', action='store_true',
                                    help=(
                                        "Be silent and accept all default values. "
                                        "This is good for debugging and automation, but "
                                        "probably not what you want"
                                    ))
    parser_interactive.set_defaults(func=interactive)

    parser_substitute = subparsers.add_parser('substitute')
    parser_substitute.add_argument('src', help="Template source directory")
    parser_substitute.add_argument('dst', help="Destination configuration directory")
    parser_substitute.set_defaults(func=substitute)

    args = parser.parse_args()
    args.func(args)

def load_config(args):
    if os.path.exists(args.config):
        with open(args.config) as f:
            return json.load(f)
    return {}

def interactive(args):
    print("\n====================================")
    print("      Interactive configuration ")
    print("====================================")

    configurator = Configurator(**load_config(args))
    if args.silent or os.environ.get('SILENT'):
        configurator.mute()
    configurator.add(
        'LMS_HOST', "Your website domain name for students (LMS).", 'www.myopenedx.com'
    ).add(
        'CMS_HOST', "Your website domain name for teachers (CMS).", 'studio.' + configurator.get('LMS_HOST')
    ).add(
        'PLATFORM_NAME', "Your platform name/title", "My Open edX"
    ).add(
        'CONTACT_EMAIL', "Your public contact email address", 'contact@' + configurator.get('LMS_HOST')
    ).add(
        'SECRET_KEY', "", random_string(24)
    ).add(
        'MYSQL_DATABASE', "", 'openedx'
    ).add(
        'MYSQL_USERNAME', "", 'openedx'
    ).add(
        'MYSQL_PASSWORD', "", random_string(8)
    ).add(
        'MONGODB_DATABASE', "", 'openedx'
    ).add(
        'NOTES_MYSQL_DATABASE', "", 'notes',
    ).add(
        'NOTES_MYSQL_USERNAME', "", 'notes',
    ).add(
        'NOTES_MYSQL_PASSWORD', "", random_string(8)
    ).add(
        'NOTES_SECRET_KEY', "", random_string(24)
    ).add(
        'NOTES_OAUTH2_SECRET', "", random_string(24)
    ).add(
        'XQUEUE_AUTH_USERNAME', "", 'lms'
    ).add(
        'XQUEUE_AUTH_PASSWORD', "", random_string(8)
    ).add(
        'XQUEUE_MYSQL_DATABASE', "", 'xqueue',
    ).add(
        'XQUEUE_MYSQL_USERNAME', "", 'xqueue',
    ).add(
        'XQUEUE_MYSQL_PASSWORD', "", random_string(8)
    ).add(
        'XQUEUE_SECRET_KEY', "", random_string(24)
    ).add_bool(
        'ACTIVATE_NOTES', "", False
    ).add_bool(
        'ACTIVATE_HTTPS', "", False
    ).add_bool(
        'ACTIVATE_XQUEUE', "", False
    )

    # Save values
    with open(args.config, 'w') as f:
        json.dump(configurator.as_dict(), f, sort_keys=True, indent=4)
    print("\nConfiguration values were saved to ", args.config)


def substitute(args):
    config = load_config(args)

    for root, _, filenames in os.walk(args.src):
        for filename in filenames:
            if filename.startswith('.'):
                # Skip hidden files, such as files generated by the IDE
                continue
            src_file = os.path.join(root, filename)
            dst_file = os.path.join(args.dst, os.path.relpath(src_file, args.src))
            substitute_file(config, src_file, dst_file)

def substitute_file(config, src, dst):
    with codecs.open(src, encoding='utf-8') as fi:
        template = jinja2.Template(fi.read(), undefined=jinja2.StrictUndefined)
    try:
        substituted = template.render(**config)
    except jinja2.exceptions.UndefinedError as e:
        sys.stderr.write("ERROR Missing config value '{}' for template {}\n".format(e.args[0], src))
        sys.exit(1)

    dst_dir = os.path.dirname(dst)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    with codecs.open(dst, encoding='utf-8', mode='w') as fo:
        fo.write(substituted)

    # Set same permissions as original file
    os.chmod(dst, os.stat(src).st_mode)

    print("Generated file {} from template {}".format(dst, src))


def random_string(length):
    return "".join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])

if __name__ == '__main__':
    main()
