from __future__ import annotations

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


def dump_all(documents: t.Sequence[t.Any], fileobj: TextIOWrapper) -> None:
    yaml.safe_dump_all(
        documents, stream=fileobj, default_flow_style=False, allow_unicode=True
    )


def dump(content: t.Any, fileobj: TextIOWrapper) -> None:
    yaml.dump(content, stream=fileobj, default_flow_style=False, allow_unicode=True)


def dumps(content: t.Any) -> str:
    result = yaml.dump(content, default_flow_style=False, allow_unicode=True)
    assert isinstance(result, str)
    return result


def str_format(content: t.Any) -> str:
    """
    Convert a value to str.

    This is almost like json, but more convenient for printing to the standard output.
    """
    if content is True:
        return "true"
    if content is False:
        return "false"
    if content is None:
        return "null"
    return str(content)


def parse(v: t.Union[str, t.IO[str]]) -> t.Any:
    """
    Parse a yaml-formatted string.
    """
    try:
        return load(v)
    except (ParserError, ScannerError):
        pass
    return v


def parse_key_value(text: str) -> t.Optional[tuple[str, t.Any]]:
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
    elif "\n" not in value and value.startswith("#"):
        # Single-line string that starts with a pound # key
        # We need to escape the string, otherwise pound will be interpreted as a comment.
        value = f'"{value}"'
    return key, parse(value)
