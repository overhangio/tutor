from __future__ import annotations

import re
import typing as t
from _io import TextIOWrapper

import yaml
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.util import load_yaml_guess_indent
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


class YamlLayout(t.NamedTuple):
    """
    Layout of a yaml document that the round-trip loader does not carry inside
    the document itself, and that must therefore be handed back to the dumper.
    """

    sequence_indent: int = 2
    sequence_dash_offset: int = 0
    explicit_start: bool = False


def round_trip_yaml(layout: YamlLayout) -> YAML:
    """
    YAML parser/dumper that preserves comments, key order and quoting style.

    This is considerably slower than the SafeLoader used everywhere else, so it
    should only be used for the few files that users are expected to edit by
    hand, such as config.yml.
    """
    yaml_rt = YAML(typ="rt")
    yaml_rt.preserve_quotes = True
    yaml_rt.default_flow_style = False
    yaml_rt.allow_unicode = True
    yaml_rt.explicit_start = layout.explicit_start
    yaml_rt.indent(
        mapping=2,
        sequence=layout.sequence_indent,
        offset=layout.sequence_dash_offset,
    )
    # Never re-wrap long values, such as RSA private keys, onto several lines.
    yaml_rt.width = 2**16
    return yaml_rt


def load_round_trip(text: str) -> tuple[t.Any, YamlLayout]:
    """
    Load a yaml document, preserving comments, key order and quoting style.

    Return the document, along with the layout that must be passed back to
    `dump_round_trip` for the document to be written out as the user wrote it.
    """
    layout = guess_layout(text)
    return round_trip_yaml(layout).load(text), layout


def guess_layout(text: str) -> YamlLayout:
    """
    Work out how a yaml document is laid out, such that it can be written back
    the way its author wrote it.

    Note that `load_yaml_guess_indent` parses the document a second time. We
    cannot use the document that it returns, because it loads it without
    `preserve_quotes`, and passing it our own parser is only supported from
    ruamel.yaml 0.19 onwards. Parsing a file as small as config.yml twice is a
    small price to pay for not having to pin a recent ruamel.yaml.
    """
    _document, sequence_indent, dash_offset = load_yaml_guess_indent(text)
    return YamlLayout(
        sequence_indent=2 if sequence_indent is None else int(sequence_indent),
        sequence_dash_offset=0 if dash_offset is None else int(dash_offset),
        explicit_start=has_explicit_start(text),
    )


def has_explicit_start(text: str) -> bool:
    """
    Check whether a yaml document opens with an explicit "---" marker.
    """
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        return stripped == "---"
    return False


def dump_round_trip(
    content: t.Any, fileobj: t.IO[str], layout: YamlLayout = YamlLayout()
) -> None:
    """
    Dump a document loaded with `load_round_trip`, preserving its formatting.
    """
    round_trip_yaml(layout).dump(content, fileobj)


def empty_document() -> CommentedMap:
    """
    An empty document suitable for `dump_round_trip`.
    """
    return CommentedMap()


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
