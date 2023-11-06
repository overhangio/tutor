import base64
import os
import subprocess
import tempfile
import unittest
from io import StringIO
from typing import List, Tuple
from unittest.mock import MagicMock, mock_open, patch

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
        with patch("sys.platform", "win32"):
            with patch.object(utils, "get_user_id", return_value=42):
                self.assertFalse(utils.is_root())
            with patch.object(utils, "get_user_id", return_value=0):
                self.assertFalse(utils.is_root())

        with patch("sys.platform", "linux"):
            with patch.object(utils, "get_user_id", return_value=42):
                self.assertFalse(utils.is_root())
            with patch.object(utils, "get_user_id", return_value=0):
                self.assertTrue(utils.is_root())

    @patch("sys.platform", "win32")
    def test_is_root_win32(self) -> None:
        result = utils.is_root()
        self.assertFalse(result)

    def test_get_user_id(self) -> None:
        with patch("os.getuid", return_value=42):
            self.assertEqual(42, utils.get_user_id())

            with patch("sys.platform", new="win32"):
                self.assertEqual(0, utils.get_user_id())

    @patch("sys.platform", "win32")
    def test_get_user_id_win32(self) -> None:
        result = utils.get_user_id()
        self.assertEqual(0, result)

    @patch("sys.stdout", new_callable=StringIO)
    @patch("subprocess.Popen", autospec=True)
    def test_execute_exit_without_error(
        self, mock_popen: MagicMock, mock_stdout: StringIO
    ) -> None:
        process = mock_popen.return_value
        mock_popen.return_value.__enter__.return_value = process
        process.wait.return_value = 0
        process.communicate.return_value = ("output", "error")

        result = utils.execute("echo", "")
        self.assertEqual(0, result)
        self.assertEqual("echo ''\n", mock_stdout.getvalue())
        self.assertEqual(1, process.wait.call_count)
        process.kill.assert_not_called()

    @patch("sys.stdout", new_callable=StringIO)
    @patch("subprocess.Popen", autospec=True)
    def test_execute_nested_command(
        self, mock_popen: MagicMock, mock_stdout: StringIO
    ) -> None:
        process = mock_popen.return_value
        mock_popen.return_value.__enter__.return_value = process
        process.wait.return_value = 0
        process.communicate.return_value = ("output", "error")

        result = utils.execute("bash", "-c", "echo -n hi")
        self.assertEqual(0, result)
        self.assertEqual("bash -c 'echo -n hi'\n", mock_stdout.getvalue())
        self.assertEqual(1, process.wait.call_count)
        process.kill.assert_not_called()

    @patch("sys.stdout", new_callable=StringIO)
    @patch("subprocess.Popen", autospec=True)
    def test_execute_exit_with_error(
        self, mock_popen: MagicMock, mock_stdout: StringIO
    ) -> None:
        process = mock_popen.return_value
        mock_popen.return_value.__enter__.return_value = process
        process.wait.return_value = 1
        process.communicate.return_value = ("output", "error")

        self.assertRaises(exceptions.TutorError, utils.execute, "echo", "")
        self.assertEqual("echo ''\n", mock_stdout.getvalue())
        self.assertEqual(1, process.wait.call_count)
        process.kill.assert_not_called()

    @patch("sys.stdout", new_callable=StringIO)
    @patch("subprocess.Popen", autospec=True)
    def test_execute_throw_exception(
        self, mock_popen: MagicMock, mock_stdout: StringIO
    ) -> None:
        process = mock_popen.return_value
        mock_popen.return_value.__enter__.return_value = process
        process.wait.side_effect = ZeroDivisionError("Exception occurred.")

        self.assertRaises(ZeroDivisionError, utils.execute, "echo", "")
        self.assertEqual("echo ''\n", mock_stdout.getvalue())
        self.assertEqual(2, process.wait.call_count)
        process.kill.assert_called_once()

    @patch("sys.stdout", new_callable=StringIO)
    @patch("subprocess.Popen", autospec=True)
    def test_execute_keyboard_interrupt(
        self, mock_popen: MagicMock, mock_stdout: StringIO
    ) -> None:
        process = mock_popen.return_value
        mock_popen.return_value.__enter__.return_value = process
        process.wait.side_effect = KeyboardInterrupt()

        with self.assertRaises(KeyboardInterrupt):
            utils.execute("echo", "")
        output = mock_stdout.getvalue()
        self.assertIn("echo", output)
        self.assertEqual(2, process.wait.call_count)
        process.kill.assert_called_once()

    @patch("sys.platform", "win32")
    def test_check_macos_docker_memory_win32_should_skip(self) -> None:
        utils.check_macos_docker_memory()

    @patch("sys.platform", "darwin")
    def test_check_macos_docker_memory_darwin(self) -> None:
        with patch("tutor.utils.open", mock_open(read_data='{"memoryMiB": 4096}')):
            utils.check_macos_docker_memory()

    @patch("sys.platform", "darwin")
    def test_check_macos_docker_memory_darwin_filenotfound(self) -> None:
        with patch("tutor.utils.open", mock_open()) as mock_open_settings:
            mock_open_settings.return_value.__enter__.side_effect = FileNotFoundError
            with self.assertRaises(exceptions.TutorError) as e:
                utils.check_macos_docker_memory()
            self.assertIn("Error accessing Docker settings file", e.exception.args[0])

    @patch("sys.platform", "darwin")
    def test_check_macos_docker_memory_darwin_json_decode_error(self) -> None:
        with patch("tutor.utils.open", mock_open(read_data="invalid")):
            with self.assertRaises(exceptions.TutorError) as e:
                utils.check_macos_docker_memory()
            self.assertIn("invalid JSON", e.exception.args[0])

    @patch("sys.platform", "darwin")
    def test_check_macos_docker_memory_darwin_key_error(self) -> None:
        with patch("tutor.utils.open", mock_open(read_data="{}")):
            with self.assertRaises(exceptions.TutorError) as e:
                utils.check_macos_docker_memory()
            self.assertIn("key 'memoryMiB' not found", e.exception.args[0])

    @patch("sys.platform", "darwin")
    def test_check_macos_docker_memory_darwin_type_error(self) -> None:
        with patch(
            "tutor.utils.open", mock_open(read_data='{"memoryMiB": "invalidstring"}')
        ):
            with self.assertRaises(exceptions.TutorError) as e:
                utils.check_macos_docker_memory()
            self.assertIn("Unexpected JSON data", e.exception.args[0])

    @patch("sys.platform", "darwin")
    def test_check_macos_docker_memory_darwin_insufficient_memory(self) -> None:
        with patch("tutor.utils.open", mock_open(read_data='{"memoryMiB": 4095}')):
            with self.assertRaises(exceptions.TutorError) as e:
                utils.check_macos_docker_memory()
            self.assertEqual(
                "Docker is configured to allocate 4095 MiB RAM, less than the recommended 4096 MiB",
                e.exception.args[0],
            )

    @patch("sys.platform", "darwin")
    def test_check_macos_docker_memory_darwin_encoding_error(self) -> None:
        with patch("tutor.utils.open", mock_open()) as mock_open_settings:
            mock_open_settings.return_value.__enter__.side_effect = TypeError
            with self.assertRaises(exceptions.TutorError) as e:
                utils.check_macos_docker_memory()
            self.assertIn("Text encoding error", e.exception.args[0])

    def test_is_http(self) -> None:
        self.assertTrue(utils.is_http("http://overhang.io/tutor/main"))
        self.assertTrue(utils.is_http("https://overhang.io/tutor/main"))
        self.assertFalse(utils.is_http("/home/user/"))
        self.assertFalse(utils.is_http("home/user/"))
        self.assertFalse(utils.is_http("http-home/user/"))

    @patch("subprocess.run")
    def test_is_docker_rootless(self, mock_run: MagicMock) -> None:
        # Mock rootless `docker info` output
        utils.is_docker_rootless.cache_clear()
        mock_run.return_value.stdout = "some prefix\n rootless foo bar".encode("utf-8")
        self.assertTrue(utils.is_docker_rootless())

        # Mock regular `docker info` output
        utils.is_docker_rootless.cache_clear()
        mock_run.return_value.stdout = "some prefix, regular docker".encode("utf-8")
        self.assertFalse(utils.is_docker_rootless())

    @patch("subprocess.run")
    def test_is_docker_rootless_podman(self, mock_run: MagicMock) -> None:
        """Test the `is_docker_rootless` when podman is used or any other error with `docker info`"""
        utils.is_docker_rootless.cache_clear()
        mock_run.side_effect = subprocess.CalledProcessError(1, "docker info")
        self.assertFalse(utils.is_docker_rootless())

    def test_format_table(self) -> None:
        rows: List[Tuple[str, ...]] = [
            ("a", "xyz", "value 1"),
            ("abc", "x", "value 12345"),
        ]
        formatted = utils.format_table(rows, separator="  ")
        self.assertEqual(
            """
a    xyz  value 1
abc  x    value 12345
""".strip(),
            formatted,
        )
