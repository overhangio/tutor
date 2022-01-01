import os
import sys
import base64
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from io import StringIO
from tutor import exceptions, utils


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

    def test_encrypt_success(self) -> None:
        password = "passw0rd"
        encrypted1 = utils.encrypt(password)
        encrypted2 = utils.encrypt(password)
        self.assertNotEqual(encrypted1, encrypted2)
        self.assertTrue(utils.verify_encrypted(encrypted1, password))
        self.assertTrue(utils.verify_encrypted(encrypted2, password))

    def test_encrypt_fail(self) -> None:
        password = "passw0rd"
        self.assertFalse(utils.verify_encrypted(password, password))

    def test_ensure_file_directory_exists(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            tempPath = os.path.join(root, "tempDir", "tempFile")
            utils.ensure_file_directory_exists(tempPath)
            self.assertTrue(os.path.exists(os.path.dirname(tempPath)))

    def test_ensure_file_directory_exists_dirExists(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            tempPath = os.path.join(root, "tempDir")
            os.makedirs(tempPath)
            self.assertRaises(
                exceptions.TutorError, utils.ensure_file_directory_exists, tempPath
            )

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

    def test_is_root(self) -> None:
        result = utils.is_root()
        self.assertFalse(result)

    @patch("sys.platform", "win32")
    def test_is_root_win32(self) -> None:
        result = utils.is_root()
        self.assertFalse(result)

    def test_get_user_id(self) -> None:
        result = utils.get_user_id()
        if sys.platform == "win32":
            self.assertEqual(0, result)
        else:
            self.assertNotEqual(0, result)

    @patch("sys.platform", "win32")
    def test_get_user_id_win32(self) -> None:
        result = utils.get_user_id()
        self.assertEqual(0, result)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("subprocess.Popen", autospec=True)
    def test_execute_exit_without_error(
        self, mock_popen: MagicMock, mock_stdout: StringIO
    ) -> None:
        process = mock_popen.return_value.__enter__.return_value
        process.returncode = 0
        process.communicate.return_value = ("output", "error")

        result = utils.execute("echo", "")
        self.assertEqual(0, result)
        self.assertEqual("echo \n", mock_stdout.getvalue())
        process.communicate.assert_called_once()
        process.wait.assert_not_called()
        process.kill.assert_not_called()

    @patch("sys.stdout", new_callable=StringIO)
    @patch("subprocess.Popen", autospec=True)
    def test_execute_exit_with_error(
        self, mock_popen: MagicMock, mock_stdout: StringIO
    ) -> None:
        process = mock_popen.return_value.__enter__.return_value
        process.returncode = 1
        process.communicate.return_value = ("output", "error")

        self.assertRaises(exceptions.TutorError, utils.execute, "echo", "")
        self.assertEqual("echo \n", mock_stdout.getvalue())
        process.communicate.assert_called_once()
        process.wait.assert_not_called()
        process.kill.assert_not_called()

    @patch("sys.stdout", new_callable=StringIO)
    @patch("subprocess.Popen", autospec=True)
    def test_execute_throw_exception(
        self, mock_popen: MagicMock, mock_stdout: StringIO
    ) -> None:
        process = mock_popen.return_value.__enter__.return_value
        process.returncode = 1
        process.communicate.side_effect = Exception("Exception occurred.")

        self.assertRaises(exceptions.TutorError, utils.execute, "echo", "")
        self.assertEqual("echo \n", mock_stdout.getvalue())
        process.communicate.assert_called_once()
        process.wait.assert_called_once()
        process.kill.assert_called_once()

    @patch("subprocess.Popen", autospec=True)
    def test_execute_keyboard_interrupt(self, mock_popen: MagicMock) -> None:
        process = mock_popen.return_value.__enter__.return_value
        process.returncode = 1
        process.communicate.side_effect = KeyboardInterrupt()

        with self.assertRaises(KeyboardInterrupt):
            utils.execute("echo", "")
        process.communicate.assert_called_once()
        process.wait.assert_called_once()
        process.kill.assert_called_once()

    @patch("sys.platform", "win32")
    def test_check_macos_memory_win32_should_skip(self) -> None:
        utils.check_macos_memory()

    @patch("sys.platform", "darwin")
    def test_check_macos_memory_darwin_filenotfound(self) -> None:
        self.assertRaises(exceptions.TutorError, utils.check_macos_memory)
