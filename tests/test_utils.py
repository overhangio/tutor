import unittest

from tutor import utils
from tutor import serialize


class UtilsTests(unittest.TestCase):
    def test_common_domain(self):
        self.assertEqual(
            "domain.com", utils.common_domain("sub1.domain.com", "sub2.domain.com")
        )
        self.assertEqual(
            "sub1.domain.com",
            utils.common_domain("sub1.domain.com", "sub2.sub1.domain.com"),
        )
        self.assertEqual("com", utils.common_domain("domain1.com", "domain2.com"))
        self.assertEqual(
            "domain.com", utils.common_domain("sub.domain.com", "ub.domain.com")
        )

    def test_reverse_host(self):
        self.assertEqual("com.google.www", utils.reverse_host("www.google.com"))


class SerializeTests(unittest.TestCase):
    def test_parse_value(self):
        self.assertEqual(True, serialize.parse_value("true"))
        self.assertEqual(False, serialize.parse_value("false"))
        self.assertEqual(None, serialize.parse_value("null"))
