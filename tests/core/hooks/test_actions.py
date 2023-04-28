import typing as t
import unittest

from tutor.core.hooks import actions, contexts


class PluginActionsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.side_effect_int = 0

    def run(self, result: t.Any = None) -> t.Any:
        with contexts.enter("tests"):
            return super().run(result=result)

    def test_do(self) -> None:
        action: actions.Action[int] = actions.Action()

        @action.add()
        def _test_action_1(increment: int) -> None:
            self.side_effect_int += increment

        @action.add()
        def _test_action_2(increment: int) -> None:
            self.side_effect_int += increment * 2

        action.do(1)
        self.assertEqual(3, self.side_effect_int)

    def test_priority(self) -> None:
        action: actions.Action[[]] = actions.Action()

        @action.add(priority=2)
        def _test_action_1() -> None:
            self.side_effect_int += 4

        @action.add(priority=1)
        def _test_action_2() -> None:
            self.side_effect_int = self.side_effect_int // 2

        # Action 2 must be performed before action 1
        self.side_effect_int = 4
        action.do()
        self.assertEqual(6, self.side_effect_int)

    def test_equal_priority(self) -> None:
        action: actions.Action[[]] = actions.Action()

        @action.add(priority=2)
        def _test_action_1() -> None:
            self.side_effect_int += 4

        @action.add(priority=2)
        def _test_action_2() -> None:
            self.side_effect_int = self.side_effect_int // 2

        # Action 2 must be performed after action 1
        self.side_effect_int = 4
        action.do()
        self.assertEqual(4, self.side_effect_int)
