import typing as t

import click

from tutor import config as tutor_config
from tutor import hooks
from tutor.types import Config

# Type of the value produced by the param type `convert` method. Since click 8.4,
# `click.ParamType` is generic and must be parameterized with that type.
ParamValue = t.TypeVar("ParamValue")


class ConfigLoaderParam(click.ParamType[ParamValue]):
    """
    Convenient param child class that automatically loads the user configuration on auto-complete.
    """

    def __init__(self) -> None:
        self.root = None
        self._config: t.Optional[Config] = None

        @hooks.Actions.PROJECT_ROOT_READY.add()
        def _on_root_ready(root: str) -> None:
            self.root = root

    @property
    def config(self) -> Config:
        if self.root is None:
            return {}
        if self._config is None:
            self._config = tutor_config.load_full(self.root)
        return self._config
