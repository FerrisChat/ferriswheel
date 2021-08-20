import re

from setuptools import setup

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

# with open('requirements.txt', 'r') as f:
#     requirements = f.readlines()


with open('README.md', encoding='utf-8') as f:
    readme = f.read()

setup(
    name="ferriswheel",
    author=author,
    url="https://github.com/Cryptex-github/ferriswheel",
    project_urls={
        "Issue tracker": "https://github.com/Cryptex-github/ferriswheel/issues/new",
    },
    version=version,
    packages=[
        "ferris",
    ],
    license="MIT",
    description="An asynchronous python wrapper for ferris.chat api",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=["aiohttp"],
    extras_require={
        "docs": [
            "sphinx>=4.1.1",
            "sphinx-material",
        ],
        "performance": ["orjson>=1.3.0"],
    },
    python_requires=">=3.8.0",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Typing :: Typed',
    ],
)
