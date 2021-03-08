import re
import yaml
from yaml.parser import ParserError
from yaml.scanner import ScannerError

import click


def load(stream):
    return yaml.load(stream, Loader=yaml.SafeLoader)


def load_all(stream):
    return yaml.load_all(stream, Loader=yaml.SafeLoader)


def dump(content, fileobj):
    yaml.dump(content, stream=fileobj, default_flow_style=False)


def dumps(content):
    return yaml.dump(content, stream=None, default_flow_style=False)


def parse(v):
    """
    Parse a yaml-formatted string.
    """
    try:
        return load(v)
    except (ParserError, ScannerError):
        pass
    return v


class YamlParamType(click.ParamType):
    name = "yaml"
    PARAM_REGEXP = r"(?P<key>[a-zA-Z0-9_-]+)=(?P<value>.*)"

    def convert(self, value, param, ctx):
        match = re.match(self.PARAM_REGEXP, value)
        if not match:
            self.fail("'{}' is not of the form 'key=value'.".format(value), param, ctx)
        key = match.groupdict()["key"]
        value = match.groupdict()["value"]
        if not value:
            # Empty strings are interpreted as null values, which is incorrect.
            value = "''"
        return key, parse(value)
