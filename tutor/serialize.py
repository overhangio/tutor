import re
from typing import IO, Any, Iterator, Tuple, Union

import click
import yaml
from _io import TextIOWrapper
from yaml.parser import ParserError
from yaml.scanner import ScannerError


def load(stream: Union[str, IO[str]]) -> Any:
    return yaml.load(stream, Loader=yaml.SafeLoader)


def load_all(stream: str) -> Iterator[Any]:
    return yaml.load_all(stream, Loader=yaml.SafeLoader)


def dump(content: Any, fileobj: TextIOWrapper) -> None:
    yaml.dump(content, stream=fileobj, default_flow_style=False)


def dumps(content: Any) -> str:
    result = yaml.dump(content, default_flow_style=False)
    assert isinstance(result, str)
    return result


def parse(v: Union[str, IO[str]]) -> Any:
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
    PARAM_REGEXP = r"(?P<key>[a-zA-Z0-9_-]+)=(?P<value>(.|\n|\r)*)"

    def convert(self, value: str, param: Any, ctx: Any) -> Tuple[str, Any]:
        match = re.match(self.PARAM_REGEXP, value)
        if not match:
            self.fail("'{}' is not of the form 'key=value'.".format(value), param, ctx)
        key = match.groupdict()["key"]
        value = match.groupdict()["value"]
        if not value:
            # Empty strings are interpreted as null values, which is incorrect.
            value = "''"
        return key, parse(value)
