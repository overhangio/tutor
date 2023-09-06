import unittest

from tutor import serialize


class SerializeTests(unittest.TestCase):
    def test_parse_str(self) -> None:
        self.assertEqual("abcd", serialize.parse("abcd"))

    def test_parse_int(self) -> None:
        self.assertEqual(1, serialize.parse("1"))

    def test_parse_bool(self) -> None:
        self.assertEqual(True, serialize.parse("true"))
        self.assertEqual(False, serialize.parse("false"))

    def test_parse_null(self) -> None:
        self.assertIsNone(serialize.parse("null"))

    def test_parse_invalid_format(self) -> None:
        self.assertEqual('["abcd"', serialize.parse('["abcd"'))

    def test_parse_list(self) -> None:
        self.assertEqual(["abcd"], serialize.parse('["abcd"]'))

    def test_parse_weird_chars(self) -> None:
        self.assertEqual("*@google.com", serialize.parse("*@google.com"))

    def test_parse_empty_string(self) -> None:
        self.assertEqual("", serialize.parse("''"))

    def test_parse_key_value(self) -> None:
        self.assertEqual(("name", True), serialize.parse_key_value("name=true"))
        self.assertEqual(("name", "abcd"), serialize.parse_key_value("name=abcd"))
        self.assertEqual(("name", ""), serialize.parse_key_value("name="))
        self.assertIsNone(serialize.parse_key_value("name"))
        self.assertEqual(("x", "a=bcd"), serialize.parse_key_value("x=a=bcd"))
        self.assertEqual(
            ("x", {"key1": {"subkey": "value"}, "key2": {"subkey": "value"}}),
            serialize.parse_key_value(
                "x=key1:\n  subkey: value\nkey2:\n  subkey: value"
            ),
        )
        self.assertEqual(
            ("INDIGO_PRIMARY_COLOR", "#225522"),
            serialize.parse_key_value("INDIGO_PRIMARY_COLOR=#225522"),
        )

    def test_str_format(self) -> None:
        self.assertEqual("true", serialize.str_format(True))
        self.assertEqual("false", serialize.str_format(False))
        self.assertEqual("null", serialize.str_format(None))
        self.assertEqual("éü©", serialize.str_format("éü©"))
        self.assertEqual("""[1, 'abcd']""", serialize.str_format([1, "abcd"]))

    def test_load_str_format(self) -> None:
        self.assertEqual(True, serialize.load(serialize.str_format(True)))
        self.assertEqual(False, serialize.load(serialize.str_format(False)))
        self.assertEqual(None, serialize.load(serialize.str_format(None)))
        self.assertEqual("éü©", serialize.load(serialize.str_format("éü©")))
        self.assertEqual([1, "abcd"], serialize.load(serialize.str_format([1, "abcd"])))
