import yaml
from yaml.parser import ParserError
from yaml.scanner import ScannerError


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
