from __future__ import annotations

import typing as t

import click.testing

from tests.helpers import TestContext, temporary_root
from tutor.commands.cli import cli


class TestCommandMixin:
    """
    Run CLI tests in an isolated test root.
    """

    @staticmethod
    def invoke(args: list[str], stdin: t.Optional[str] = None) -> click.testing.Result:
        with temporary_root() as root:
            return TestCommandMixin.invoke_in_root(root, args, stdin=stdin)

    @staticmethod
    def invoke_in_root(
        root: str,
        args: list[str],
        catch_exceptions: bool = True,
        stdin: t.Optional[str] = None,
    ) -> click.testing.Result:
        """
        Use this method for commands that all need to run in the same root:

            with temporary_root() as root:
                result1 = self.invoke_in_root(root, ...)
                result2 = self.invoke_in_root(root, ...)

        Commands that prompt the user must be fed their answers with `stdin`: on
        end of input, click aborts instead of falling back to the prompt defaults.
        """
        runner = click.testing.CliRunner(
            env={
                "TUTOR_ROOT": root,
                "TUTOR_IGNORE_ENTRYPOINT_PLUGINS": "1",
                "TUTOR_IGNORE_DICT_PLUGINS": "1",
            },
        )
        return runner.invoke(
            cli,
            args,
            obj=TestContext(root),
            catch_exceptions=catch_exceptions,
            input=stdin,
        )
