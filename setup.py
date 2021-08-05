from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    readme = f.read()

setup(
    name="ferrischat.py",
    author="Cryptex",
    url="https://github.com/Cryptex-github/ferrischat.py",
    project_urls={
        "Issue tracker": "https://github.com/Cryptex-github/ferrischat.py/new/main",
    },
    version="0.0.0", # 0.1.0 for the finished release
    packages=[
        "ferris",
    ],
    license="MIT",
    description="An asynchronous python wrapper for ferris.chat api",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    extras_require={
        "docs": [
            "sphinx>=4.1.1",
            "furo",
        ],
        "performance": [
            "orjson>=1.3.0"
        ]
    },
    python_requires=">=3.8.0",
    classifiers=[
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
    ]
)
