from __future__ import annotations

import typing as t
import unittest

from tutor.core.hooks import contexts, filters


class PluginFiltersTests(unittest.TestCase):
    def run(self, result: t.Any = None) -> t.Any:
        with contexts.enter("tests"):
            return super().run(result=result)

    def test_add(self) -> None:
        filtre: filters.Filter[int, []] = filters.Filter()

        @filtre.add()
        def filter1(value: int) -> int:
            return value + 1

        value = filtre.apply(0)
        self.assertEqual(1, value)

    def test_add_items(self) -> None:
        filtre: filters.Filter[list[int], []] = filters.Filter()

        @filtre.add()
        def filter1(sheeps: list[int]) -> list[int]:
            return sheeps + [0]

        filtre.add_item(1)
        filtre.add_item(2)
        filtre.add_items([3, 4])

        sheeps: list[int] = filtre.apply([])
        self.assertEqual([0, 1, 2, 3, 4], sheeps)

    def test_filter_callbacks(self) -> None:
        callback = filters.FilterCallback(lambda _: 1)
        self.assertTrue(callback.is_in_context(None))
        self.assertFalse(callback.is_in_context("customcontext"))
        self.assertEqual(1, callback.apply(0))

    def test_filter_context(self) -> None:
        filtre: filters.Filter[list[int], []] = filters.Filter()
        with contexts.enter("testcontext"):
            filtre.add_item(1)
        filtre.add_item(2)

        self.assertEqual([1, 2], filtre.apply([]))
        self.assertEqual([1], filtre.apply_from_context("testcontext", []))

    def test_clear_context(self) -> None:
        filtre: filters.Filter[list[int], []] = filters.Filter()
        with contexts.enter("testcontext"):
            filtre.add_item(1)
        filtre.add_item(2)

        self.assertEqual([1, 2], filtre.apply([]))
        filtre.clear(context="testcontext")
        self.assertEqual([2], filtre.apply([]))
