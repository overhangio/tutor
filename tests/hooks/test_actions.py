import typing as t
import unittest

from tutor import hooks


class PluginActionsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.side_effect_int = 0

    def tearDown(self) -> None:
        super().tearDown()
        hooks.actions.clear_all(context="tests")

    def run(self, result: t.Any = None) -> t.Any:
        with hooks.contexts.enter("tests"):
            return super().run(result=result)

    def test_on(self) -> None:
        @hooks.actions.add("test-action")
        def _test_action_1(increment: int) -> None:
            self.side_effect_int += increment

        @hooks.actions.add("test-action")
        def _test_action_2(increment: int) -> None:
            self.side_effect_int += increment * 2

        hooks.actions.do("test-action", 1)
        self.assertEqual(3, self.side_effect_int)

    def test_priority(self) -> None:
        @hooks.actions.add("test-action", priority=2)
        def _test_action_1() -> None:
            self.side_effect_int += 4

        @hooks.actions.add("test-action", priority=1)
        def _test_action_2() -> None:
            self.side_effect_int = self.side_effect_int // 2

        # Action 2 must be performed before action 1
        self.side_effect_int = 4
        hooks.actions.do("test-action")
        self.assertEqual(6, self.side_effect_int)

    def test_equal_priority(self) -> None:
        @hooks.actions.add("test-action", priority=2)
        def _test_action_1() -> None:
            self.side_effect_int += 4

        @hooks.actions.add("test-action", priority=2)
        def _test_action_2() -> None:
            self.side_effect_int = self.side_effect_int // 2

        # Action 2 must be performed after action 1
        self.side_effect_int = 4
        hooks.actions.do("test-action")
        self.assertEqual(4, self.side_effect_int)
