import unittest

from tutor import serialize


class SerializeTests(unittest.TestCase):
    def test_parse_str(self):
        self.assertEqual("abcd", serialize.parse("abcd"))

    def test_parse_int(self):
        self.assertEqual(1, serialize.parse("1"))

    def test_parse_bool(self):
        self.assertEqual(True, serialize.parse("true"))
        self.assertEqual(False, serialize.parse("false"))

    def test_parse_null(self):
        self.assertIsNone(serialize.parse("null"))

    def test_parse_invalid_format(self):
        self.assertEqual('["abcd"', serialize.parse('["abcd"'))

    def test_parse_list(self):
        self.assertEqual(["abcd"], serialize.parse('["abcd"]'))

    def test_parse_weird_chars(self):
        self.assertEqual("*@google.com", serialize.parse("*@google.com"))
