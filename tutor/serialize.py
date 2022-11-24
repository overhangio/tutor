import re
import typing as t

import yaml
from _io import TextIOWrapper
from yaml.parser import ParserError
from yaml.scanner import ScannerError


def load(stream: t.Union[str, t.IO[str]]) -> t.Any:
    return yaml.load(stream, Loader=yaml.SafeLoader)


def load_all(stream: str) -> t.Iterator[t.Any]:
    return yaml.load_all(stream, Loader=yaml.SafeLoader)


def dump(content: t.Any, fileobj: TextIOWrapper) -> None:
    yaml.dump(content, stream=fileobj, default_flow_style=False)


def dumps(content: t.Any) -> str:
    result = yaml.dump(content, default_flow_style=False)
    assert isinstance(result, str)
    return result


def parse(v: t.Union[str, t.IO[str]]) -> t.Any:
    """
    Parse a yaml-formatted string.
    """
    try:
        return load(v)
    except (ParserError, ScannerError):
        pass
    return v


def parse_key_value(text: str) -> t.Optional[t.Tuple[str, t.Any]]:
    """
    Parse <KEY>=<YAML VALUE> command line arguments.

    Return None if text could not be parsed.
    """
    match = re.match(r"(?P<key>[a-zA-Z0-9_-]+)=(?P<value>(.|\n|\r)*)", text)
    if not match:
        return None
    key = match.groupdict()["key"]
    value = match.groupdict()["value"]
    if not value:
        # Empty strings are interpreted as null values, which is incorrect.
        value = "''"
    return key, parse(value)
