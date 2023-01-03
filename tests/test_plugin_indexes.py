import os
import unittest
from unittest.mock import patch

from tutor.exceptions import TutorError
from tutor.plugins import indexes
from tutor.types import Config


class PluginIndexesTest(unittest.TestCase):
    def test_named_index_url(self) -> None:
        self.assertEqual(
            f"https://myindex.com/tutor/{indexes.RELEASE}/plugins.yml",
            indexes.named_index_url("https://myindex.com/tutor"),
        )
        self.assertEqual(
            f"https://myindex.com/tutor/{indexes.RELEASE}/plugins.yml",
            indexes.named_index_url("https://myindex.com/tutor/"),
        )

        local_url = os.path.join("path", "to", "index", indexes.RELEASE)
        self.assertEqual(
            os.path.join(local_url, indexes.RELEASE, "plugins.yml"),
            indexes.named_index_url(local_url),
        )

    def test_parse_index(self) -> None:
        # Valid, empty index
        self.assertEqual([], indexes.parse_index("[]"))
        # Invalid index, list expected
        with self.assertRaises(TutorError):
            self.assertEqual([], indexes.parse_index("{}"))
        # Invalid, empty index
        with self.assertRaises(TutorError):
            self.assertEqual([], indexes.parse_index("["))
        # Partially valid index
        with patch.object(indexes.fmt, "echo"):
            self.assertEqual(
                [{"name": "valid1"}],
                indexes.parse_index(
                    """
- namE: invalid1
- name: valid1
        """
                ),
            )

    def test_add(self) -> None:
        config: Config = {}
        self.assertTrue(indexes.add("https://myindex.com", config))
        self.assertFalse(indexes.add("https://myindex.com", config))
        self.assertEqual(["https://myindex.com"], config["PLUGIN_INDEXES"])

    def test_add_by_alias(self) -> None:
        config: Config = {}
        self.assertTrue(indexes.add("main", config))
        self.assertEqual(["https://overhang.io/tutor/main"], config["PLUGIN_INDEXES"])
        self.assertTrue(indexes.remove("main", config))
        self.assertEqual([], config["PLUGIN_INDEXES"])

    def test_deduplication(self) -> None:
        plugins = [
            {"name": "plugin1", "description": "desc1"},
            {"name": "PLUGIN1", "description": "desc2"},
        ]
        deduplicated = indexes.deduplicate_plugins(plugins)
        self.assertEqual([{"name": "plugin1", "description": "desc2"}], deduplicated)

    def test_short_description(self) -> None:
        entry = indexes.IndexEntry({"name": "plugin1"})
        self.assertEqual("", entry.short_description)

    def test_entry_match(self) -> None:
        self.assertTrue(indexes.IndexEntry({"name": "ecommerce"}).match("ecomm"))
        self.assertFalse(indexes.IndexEntry({"name": "ecommerce"}).match("ecom1"))
        self.assertTrue(indexes.IndexEntry({"name": "ecommerce"}).match("Ecom"))
        self.assertTrue(
            indexes.IndexEntry(
                {"name": "ecommerce", "description": "An awesome plugin"}
            ).match("AWESOME")
        )
