from crypt import crypt
from hmac import compare_digest
import json
import os
import random
import shutil
import string
import subprocess
import sys

import click

from . import exceptions
from . import fmt


def encrypt(text):
    """
    Encrypt some textual content. The method employed is the same as suggested in the
    `python docs <https://docs.python.org/3/library/crypt.html#examples>`__. The
    encryption process is compatible with the password verification performed by
    `htpasswd <https://httpd.apache.org/docs/2.4/programs/htpasswd.html>`__.
    """
    hashed = crypt(text)
    return crypt(text, hashed)


def verify_encrypted(encrypted, text):
    """
    Return True/False if the encrypted content corresponds to the unencrypted text.
    """
    return compare_digest(crypt(text, encrypted), encrypted)


def ensure_file_directory_exists(path):
    """
    Create file's base directory if it does not exist.
    """
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def random_string(length):
    return "".join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(length)]
    )


def list_if(services):
    return json.dumps([service[0] for service in services if service[1]])


def common_domain(d1, d2):
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


def reverse_host(domain):
    """
    Return the reverse domain name, java-style.

    Ex: "www.google.com" -> "com.google.www"
    """
    return ".".join(domain.split(".")[::-1])


def walk_files(path):
    """
    Iterate on file paths located in directory.
    """
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            yield os.path.join(dirpath, filename)


def docker_run(*command):
    args = ["run", "--rm"]
    if is_a_tty():
        args.append("-it")
    return docker(*args, *command)


def docker(*command):
    if shutil.which("docker") is None:
        raise exceptions.TutorError(
            "docker is not installed. Please follow instructions from https://docs.docker.com/install/"
        )
    return execute("docker", *command)


def docker_compose(*command):
    if shutil.which("docker-compose") is None:
        raise exceptions.TutorError(
            "docker-compose is not installed. Please follow instructions from https://docs.docker.com/compose/install/"
        )
    return execute("docker-compose", *command)


def kubectl(*command):
    if shutil.which("kubectl") is None:
        raise exceptions.TutorError(
            "kubectl is not installed. Please follow instructions from https://kubernetes.io/docs/tasks/tools/install-kubectl/"
        )
    return execute("kubectl", *command)


def is_a_tty():
    """
    Return True if stdin is able to allocate a tty. Tty allocation sometimes cannot be
    enabled, for instance in cron jobs
    """
    return os.isatty(sys.stdin.fileno())


def execute(*command):
    click.echo(fmt.command(" ".join(command)))
    with subprocess.Popen(command) as p:
        try:
            result = p.wait(timeout=None)
        except KeyboardInterrupt:
            p.kill()
            p.wait()
            raise
        except Exception:
            p.kill()
            p.wait()
            raise exceptions.TutorError("Command failed: {}".format(" ".join(command)))
        if result > 0:
            raise exceptions.TutorError(
                "Command failed with status {}: {}".format(result, " ".join(command))
            )


def check_output(*command):
    click.echo(fmt.command(" ".join(command)))
    try:
        return subprocess.check_output(command)
    except:
        fmt.echo_error("Command failed: {}".format(" ".join(command)))
        raise
