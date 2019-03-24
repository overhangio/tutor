import io
import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, "README.rst"), "rt", encoding="utf8") as f:
    readme = f.read()

about = {}
with io.open(os.path.join(here, "tutor", "__about__.py"), "rt", encoding="utf-8") as f:
    exec(f.read(), about)

setup(
    name="tutor-openedx",
    version=about["__version__"],
    url="https://docs.tutor.overhang.io/",
    project_urls={
        "Documentation": "https://docs.tutor.overhang.io/",
        "Code": "https://github.com/regisb/tutor",
        "Issue tracker": "https://github.com/regisb/tutor/issues",
        "Community": "https://discuss.overhang.io",
    },
    license="AGPLv3",
    author="Régis Behmo",
    author_email="regis@behmo.com",
    description="The Open edX distribution for the busy system administrator",
    long_description=readme,
    packages=["tutor"],
    include_package_data=True,
    python_requires=">=3.5",
    install_requires=[
        "appdirs",
        "click>=7.0",
        "click_repl",
        "jinja2",
        "kubernetes",
        "pyyaml"
    ],
    entry_points={
        'console_scripts': [
            'tutor=tutor.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
