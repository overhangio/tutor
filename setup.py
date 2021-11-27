import io
import os
from setuptools import find_packages, setup
from typing import List

HERE = os.path.abspath(os.path.dirname(__file__))


def load_readme():
    with io.open(os.path.join(HERE, "README.rst"), "rt", encoding="utf8") as f:
        readme = f.read()
    # Replace img src for publication on pypi
    return readme.replace(
        "./docs/img/", "https://github.com/overhangio/tutor/raw/master/docs/img/"
    )


def load_about():
    about = {}
    with io.open(
        os.path.join(HERE, "tutor", "__about__.py"), "rt", encoding="utf-8"
    ) as f:
        exec(f.read(), about)  # pylint: disable=exec-used
    return about


def load_requirements() -> List[str]:
    with io.open(
        os.path.join(HERE, "requirements", "base.in"), "rt", encoding="utf-8"
    ) as f:
        return [line.strip() for line in f if is_requirement(line)]


def load_dev_requirements() -> List[str]:
    with io.open(
        os.path.join(HERE, "requirements", "dev.in"), "rt", encoding="utf-8"
    ) as f:
        return [line.strip() for line in f if is_requirement(line)]


def is_requirement(line):
    return not (line.strip() == "" or line.startswith("#") or line.startswith("-"))


ABOUT = load_about()

setup(
    name="tutor",
    version=ABOUT["__version__"],
    url="https://docs.tutor.overhang.io/",
    project_urls={
        "Documentation": "https://docs.tutor.overhang.io/",
        "Code": "https://github.com/overhangio/tutor",
        "Issue tracker": "https://github.com/overhangio/tutor/issues",
        "Community": "https://discuss.overhang.io",
    },
    license="AGPLv3",
    author="Overhang.io",
    author_email="contact@overhang.io",
    description="The Docker-based Open edX distribution designed for peace of mind",
    long_description=load_readme(),
    long_description_content_type="text/x-rst",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    python_requires=">=3.5",
    install_requires=load_requirements(),
    entry_points={"console_scripts": ["tutor=tutor.commands.cli:main"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    tests_require=load_dev_requirements(),
    test_suite="tests",
)
