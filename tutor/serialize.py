import yaml
from yaml.parser import ParserError


def load(stream):
    return yaml.load(stream, Loader=yaml.SafeLoader)


def dump(content, fileobj):
    yaml.dump(content, fileobj, default_flow_style=False)


def parse(v):
    """
    Parse a yaml-formatted string.
    """
    try:
        return load(v)
    except ParserError:
        pass
    return v
