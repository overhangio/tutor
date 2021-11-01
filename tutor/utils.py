import base64
import json
import os
import random
import shutil
import string
import struct
import subprocess
import sys
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
            "Attempting to create a directory, but a file with the same name already exists: {}".format(
                directory
            )
        )
    if os.path.isdir(path):
        raise exceptions.TutorError(
            "Attempting to write to a file, but a directory with the same name already exists: {}".format(
                directory
            )
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
    data = struct.pack("%sB" % len(bys), *bys)
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
    if sys.platform == "win32":
        # Don't even try
        return 0
    return os.getuid()


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


def docker_compose(*command: str) -> int:
    if shutil.which("docker-compose") is None:
        raise exceptions.TutorError(
            "docker-compose is not installed. Please follow instructions from https://docs.docker.com/compose/install/"
        )
    return execute("docker-compose", *command)


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
    return os.isatty(sys.stdin.fileno())


def execute(*command: str) -> int:
    click.echo(fmt.command(" ".join(command)))
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
            raise exceptions.TutorError(
                "Command failed: {}".format(" ".join(command))
            ) from e
        if result > 0:
            raise exceptions.TutorError(
                "Command failed with status {}: {}".format(result, " ".join(command))
            )
    return result


def check_output(*command: str) -> bytes:
    click.echo(fmt.command(" ".join(command)))
    try:
        return subprocess.check_output(command)
    except Exception as e:
        raise exceptions.TutorError(
            "Command failed: {}".format(" ".join(command))
        ) from e


def check_macos_memory() -> None:
    """
    Try to check that the RAM allocated to the Docker VM on macOS is at least 4 GB.
    """
    if sys.platform != "darwin":
        return

    settings_path = os.path.expanduser(
        "~/Library/Group Containers/group.com.docker/settings.json"
    )

    try:
        with open(settings_path) as fp:
            data = json.load(fp)
            memory_mib = int(data["memoryMiB"])
    except OSError as e:
        raise exceptions.TutorError(
            "Error accessing {}: [{}] {}".format(settings_path, e.errno, e.strerror)
        ) from e
    except json.JSONDecodeError as e:
        raise exceptions.TutorError(
            "Error reading {}: invalid JSON: {} [{}:{}]".format(
                settings_path, e.msg, e.lineno, e.colno
            )
        ) from e
    except (ValueError, TypeError, OverflowError) as e:
        # ValueError from open() indicates an encoding error
        raise exceptions.TutorError(
            "Text encoding error or unexpected JSON data: in {}: {}".format(
                settings_path, str(e)
            )
        ) from e
    except KeyError as e:
        # Value is absent (Docker creates the file with the default setting of 2048 explicitly
        # written in, so we shouldn't need to assume a default value here.)
        raise exceptions.TutorError(
            "key 'memoryMiB' not found in {}".format(settings_path)
        ) from e

    if memory_mib < 4096:
        raise exceptions.TutorError(
            "Docker is configured to allocate {} MiB RAM, less than the recommended {} MiB".format(
                memory_mib, 4096
            )
        )
