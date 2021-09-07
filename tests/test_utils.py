import base64
import unittest

from tutor import utils


class UtilsTests(unittest.TestCase):
    def test_common_domain(self) -> None:
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

    def test_reverse_host(self) -> None:
        self.assertEqual("com.google.www", utils.reverse_host("www.google.com"))

    def test_list_if(self) -> None:
        self.assertEqual('["cms"]', utils.list_if([("lms", False), ("cms", True)]))

    def test_encrypt_decrypt(self) -> None:
        password = "passw0rd"
        encrypted1 = utils.encrypt(password)
        encrypted2 = utils.encrypt(password)
        self.assertNotEqual(encrypted1, encrypted2)
        self.assertTrue(utils.verify_encrypted(encrypted1, password))
        self.assertTrue(utils.verify_encrypted(encrypted2, password))

    def test_long_to_base64(self) -> None:
        self.assertEqual(
            b"\x00", base64.urlsafe_b64decode(utils.long_to_base64(0) + "==")
        )

    def test_rsa_key(self) -> None:
        key = utils.rsa_private_key(1024)
        imported = utils.rsa_import_key(key)
        self.assertIsNotNone(imported.e)
        self.assertIsNotNone(imported.d)
        self.assertIsNotNone(imported.n)
        self.assertIsNotNone(imported.p)
        self.assertIsNotNone(imported.q)
