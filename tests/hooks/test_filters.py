import typing as t
import unittest

from tutor import hooks


class PluginFiltersTests(unittest.TestCase):
    def tearDown(self) -> None:
        super().tearDown()
        hooks.filters.clear_all(context="tests")

    def run(self, result: t.Any = None) -> t.Any:
        with hooks.contexts.enter("tests"):
            return super().run(result=result)

    def test_add(self) -> None:
        @hooks.filters.add("tests:count-sheeps")
        def filter1(value: int) -> int:
            return value + 1

        value = hooks.filters.apply("tests:count-sheeps", 0)
        self.assertEqual(1, value)

    def test_add_items(self) -> None:
        @hooks.filters.add("tests:add-sheeps")
        def filter1(sheeps: t.List[int]) -> t.List[int]:
            return sheeps + [0]

        hooks.filters.add_item("tests:add-sheeps", 1)
        hooks.filters.add_item("tests:add-sheeps", 2)
        hooks.filters.add_items("tests:add-sheeps", [3, 4])

        sheeps: t.List[int] = hooks.filters.apply("tests:add-sheeps", [])
        self.assertEqual([0, 1, 2, 3, 4], sheeps)

    def test_filter_callbacks(self) -> None:
        callback = hooks.filters.FilterCallback(lambda _: 1)
        self.assertTrue(callback.is_in_context(None))
        self.assertFalse(callback.is_in_context("customcontext"))
        self.assertEqual(1, callback.apply(0))
        self.assertEqual(0, callback.apply(0, context="customcontext"))

    def test_filter_context(self) -> None:
        with hooks.contexts.enter("testcontext"):
            hooks.filters.add_item("test:sheeps", 1)
        hooks.filters.add_item("test:sheeps", 2)

        self.assertEqual([1, 2], hooks.filters.apply("test:sheeps", []))
        self.assertEqual(
            [1], hooks.filters.apply("test:sheeps", [], context="testcontext")
        )

    def test_clear_context(self) -> None:
        with hooks.contexts.enter("testcontext"):
            hooks.filters.add_item("test:sheeps", 1)
        hooks.filters.add_item("test:sheeps", 2)

        self.assertEqual([1, 2], hooks.filters.apply("test:sheeps", []))
        hooks.filters.clear("test:sheeps", context="testcontext")
        self.assertEqual([2], hooks.filters.apply("test:sheeps", []))
