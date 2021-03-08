import unittest

import click

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

    def test_parse_empty_string(self):
        self.assertEqual("", serialize.parse("''"))

    def test_yaml_param_type(self):
        param = serialize.YamlParamType()
        self.assertEqual(("name", True), param.convert("name=true", "param", {}))
        self.assertEqual(("name", "abcd"), param.convert("name=abcd", "param", {}))
        self.assertEqual(("name", ""), param.convert("name=", "param", {}))
        with self.assertRaises(click.exceptions.BadParameter):
            param.convert("name", "param", {})
        self.assertEqual(("x", "a=bcd"), param.convert("x=a=bcd", "param", {}))
