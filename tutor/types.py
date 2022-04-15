import typing as t

# https://mypy.readthedocs.io/en/latest/kinds_of_types.html#type-aliases
from typing_extensions import TypeAlias

from . import exceptions

ConfigValue: TypeAlias = t.Union[
    str,
    float,
    None,
    bool,
    t.List[str],
    t.List[t.Any],
    t.Dict[str, t.Any],
    t.Dict[t.Any, t.Any],
]
Config: TypeAlias = t.Dict[str, ConfigValue]


def cast_config(config: t.Any) -> Config:
    if not isinstance(config, dict):
        raise exceptions.TutorError(
            f"Invalid configuration: expected dict, got {config.__class__}"
        )
    for key in config.keys():
        if not isinstance(key, str):
            raise exceptions.TutorError(
                f"Invalid configuration: expected str, got {key.__class__} for key '{key}'"
            )
    return config


T = t.TypeVar("T")


def get_typed(
    config: Config, key: str, expected_type: t.Type[T], default: t.Optional[T] = None
) -> T:
    value = config.get(key, default)
    if not isinstance(value, expected_type):
        raise exceptions.TutorError(
            "Invalid config entry: expected {expected_type.__name__}, got {value.__class__} for key '{key}'"
        )
    return value
