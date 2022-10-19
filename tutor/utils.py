import base64
import json
import os
import random
import shlex
import shutil
import string
import struct
import subprocess
import sys
from functools import lru_cache
from typing import List, Tuple

import click
from Crypto.Protocol.KDF import bcrypt, bcrypt_check
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import RsaKey

from . import exceptions, fmt


def encrypt(text: str) -> str:
    """
    Encrypt some textual content with bcrypt.
    https://pycryptodome.readthedocs.io/en/latest/src/protocol/kdf.html#bcrypt
    The encryption process is compatible with the password verification performed by
    `htpasswd <https://httpd.apache.org/docs/2.4/programs/htpasswd.html>`__.
    """
    return bcrypt(text.encode(), 12).decode()


def verify_encrypted(encrypted: str, text: str) -> bool:
    """
    Return True/False if the encrypted content corresponds to the unencrypted text.
    """
    try:
        bcrypt_check(text.encode(), encrypted.encode())
        return True
    except ValueError:
        return False


def ensure_file_directory_exists(path: str) -> None:
    """
    Create file's base directory if it does not exist.
    """
    directory = os.path.dirname(path)
    if os.path.isfile(directory):
        raise exceptions.TutorError(
            f"Attempting to create a directory, but a file with the same name already exists: {directory}"
        )
    if os.path.isdir(path):
        raise exceptions.TutorError(
            f"Attempting to write to a file, but a directory with the same name already exists: {directory}"
        )
    if not os.path.exists(directory):
        os.makedirs(directory)


def random_string(length: int) -> str:
    return "".join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(length)]
    )


def list_if(services: List[Tuple[str, bool]]) -> str:
    return json.dumps([service[0] for service in services if service[1]])


def common_domain(d1: str, d2: str) -> str:
    """
    Return the common domain between two domain names.

    Ex: "sub1.domain.com" and "sub2.domain.com" -> "domain.com"
    """
    components1 = d1.split(".")[::-1]
    components2 = d2.split(".")[::-1]
    common = []
    for c in range(0, min(len(components1), len(components2))):
        if components1[c] == components2[c]:
            common.append(components1[c])
        else:
            break
    return ".".join(common[::-1])


def reverse_host(domain: str) -> str:
    """
    Return the reverse domain name, java-style.

    Ex: "www.google.com" -> "com.google.www"
    """
    return ".".join(domain.split(".")[::-1])


def rsa_private_key(bits: int = 2048) -> str:
    """
    Export an RSA private key in PEM format.
    """
    key = RSA.generate(bits)
    return key.export_key().decode()


def rsa_import_key(key: str) -> RsaKey:
    """
    Import PEM-formatted RSA key and return the corresponding object.
    """
    return RSA.import_key(key.encode())


def long_to_base64(n: int) -> str:
    """
    Borrowed from jwkest.__init__
    """

    def long2intarr(long_int: int) -> List[int]:
        _bytes: List[int] = []
        while long_int:
            long_int, r = divmod(long_int, 256)
            _bytes.insert(0, r)
        return _bytes

    bys = long2intarr(n)
    data = struct.pack(f"{len(bys)}B", *bys)
    if not data:
        data = b"\x00"
    s = base64.urlsafe_b64encode(data).rstrip(b"=")
    return s.decode("ascii")


def is_root() -> bool:
    """
    Check whether tutor is being run as root/sudo.
    """
    if sys.platform == "win32":
        # Don't even try
        return False
    return get_user_id() == 0


def get_user_id() -> int:
    """
    Portable way to get user ID. Note: I have no idea if it actually works on windows...
    """
    if sys.platform != "win32":
        return os.getuid()

    # Don't even try for windows
    return 0


def docker_run(*command: str) -> int:
    args = ["run", "--rm"]
    if is_a_tty():
        args.append("-it")
    return docker(*args, *command)


def docker(*command: str) -> int:
    if shutil.which("docker") is None:
        raise exceptions.TutorError(
            "docker is not installed. Please follow instructions from https://docs.docker.com/install/"
        )
    return execute("docker", *command)


@lru_cache(maxsize=None)
def _docker_compose_command() -> Tuple[str, ...]:
    """
    A helper function to determine which program to call when running docker compose
    """
    if os.environ.get("TUTOR_USE_COMPOSE_SUBCOMMAND") is not None:
        return ("docker", "compose")
    if shutil.which("docker-compose") is not None:
        return ("docker-compose",)
    if shutil.which("docker") is not None:
        if subprocess.run(["docker", "compose"], capture_output=True).returncode == 0:
            return ("docker", "compose")
    raise exceptions.TutorError(
        "docker-compose is not installed. Please follow instructions from https://docs.docker.com/compose/install/"
    )


def docker_compose(*command: str) -> int:
    return execute(*_docker_compose_command(), *command)


def kubectl(*command: str) -> int:
    if shutil.which("kubectl") is None:
        raise exceptions.TutorError(
            "kubectl is not installed. Please follow instructions from https://kubernetes.io/docs/tasks/tools/install-kubectl/"
        )
    return execute("kubectl", *command)


def is_a_tty() -> bool:
    """
    Return True if stdin is able to allocate a tty. Tty allocation sometimes cannot be
    enabled, for instance in cron jobs
    """
    return sys.stdin.isatty()


def execute(*command: str) -> int:
    click.echo(fmt.command(_shlex_join(*command)))
    return execute_silent(*command)


def execute_silent(*command: str) -> int:
    with subprocess.Popen(command) as p:
        try:
            result = p.wait(timeout=None)
        except KeyboardInterrupt:
            p.kill()
            p.wait()
            raise
        except Exception as e:
            p.kill()
            p.wait()
            raise exceptions.TutorError(f"Command failed: {' '.join(command)}") from e
        if result > 0:
            raise exceptions.TutorError(
                f"Command failed with status {result}: {' '.join(command)}"
            )
    return result


def _shlex_join(*split_command: str) -> str:
    """
    Return a shell-escaped string from *split_command.

    TODO: REMOVE THIS FUNCTION AFTER 2023-06-27.
      This function is a shim for the ``shlex.join`` standard library function,
      which becomes available in Python 3.8  The end-of-life date for Python 3.7
      is in Jan 2023 (https://endoflife.date/python). After that point, it
      would be good to delete this function and just use Py3.8's ``shlex.join``.
    """
    return " ".join(shlex.quote(arg) for arg in split_command)


def check_output(*command: str) -> bytes:
    literal_command = _shlex_join(*command)
    click.echo(fmt.command(literal_command))
    try:
        return subprocess.check_output(command)
    except Exception as e:
        raise exceptions.TutorError(f"Command failed: {literal_command}") from e


def check_macos_docker_memory() -> None:
    """
    Try to check that the RAM allocated to the Docker VM on macOS is at least 4 GB.

    Parse macOS Docker settings file from user directory and return the max
    allocated memory. Will raise TutorError in case of parsing/loading error.
    """
    if sys.platform != "darwin":
        return

    settings_path = os.path.expanduser(
        "~/Library/Group Containers/group.com.docker/settings.json"
    )

    try:
        with open(settings_path, encoding="utf-8") as fp:
            data = json.load(fp)
            memory_mib = int(data["memoryMiB"])
    except OSError as e:
        raise exceptions.TutorError(f"Error accessing Docker settings file: {e}") from e
    except json.JSONDecodeError as e:
        raise exceptions.TutorError(
            f"Error reading {settings_path}, invalid JSON: {e}"
        ) from e
    except ValueError as e:
        raise exceptions.TutorError(
            f"Unexpected JSON data in {settings_path}: {e}"
        ) from e
    except KeyError as e:
        # Value is absent (Docker creates the file with the default setting of 2048 explicitly
        # written in, so we shouldn't need to assume a default value here.)
        raise exceptions.TutorError(
            f"key 'memoryMiB' not found in {settings_path}"
        ) from e
    except (TypeError, OverflowError) as e:
        # TypeError from open() indicates an encoding error
        raise exceptions.TutorError(
            f"Text encoding error in {settings_path}: {e}"
        ) from e

    if memory_mib < 4096:
        raise exceptions.TutorError(
            f"Docker is configured to allocate {memory_mib} MiB RAM, less than the recommended {4096} MiB"
        )
