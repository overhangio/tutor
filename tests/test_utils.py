import unittest

from tutor import utils


class UtilsTests(unittest.TestCase):

    def test_common_domain(self):
        self.assertEqual("domain.com", utils.common_domain("sub1.domain.com", "sub2.domain.com"))
        self.assertEqual("sub1.domain.com", utils.common_domain("sub1.domain.com", "sub2.sub1.domain.com"))
        self.assertEqual("com", utils.common_domain("domain1.com", "domain2.com"))
        self.assertEqual("domain.com", utils.common_domain("sub.domain.com", "ub.domain.com"))

    def test_parse_yaml_value(self):
        self.assertEqual(True, utils.parse_yaml_value("true"))
        self.assertEqual(False, utils.parse_yaml_value("false"))
        self.assertEqual(None, utils.parse_yaml_value("null"))
