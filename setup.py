import pathlib
import re

from setuptools import setup

ROOT = pathlib.Path(__file__).parent

with open('ferris/__init__.py', 'r') as f:
    content = f.read()
    try:
        version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE).group(1)  # type: ignore
    except AttributeError:
        raise RuntimeError('Unable to find version string')

    try:
        author = re.search(r'^__author__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE).group(1)  # type: ignore
    except AttributeError:
        author = 'Cryptex & jay3332'


with open(ROOT / 'README.md', encoding='utf-8') as f:
    readme = f.read()

with open(ROOT / 'requirements.txt', encoding='utf-8') as f:
    requirements = f.readlines()

setup(
    name="ferriswheel",
    author=author,
    url="https://github.com/FerrisChat/ferriswheel",
    project_urls={
        "Issue tracker": "https://github.com/FerrisChat/ferriswheel/issues/new",
    },
    version=version,
    packages=["ferris", "ferris.types", "ferris.plugins", "ferris.plugins.commands"],
    license="MIT",
    description="An asynchronous Python wrapper around FerrisChat's API",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        "docs": [
            "sphinx>=4.1.1",
            "sphinx-material",
            'sphinx-copybutton',
            'readthedocs-sphinx-search',
        ],
        "performance": ["aiohttp[speedups]"],
    },
    python_requires=">=3.8.0",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Typing :: Typed',
    ],
)
