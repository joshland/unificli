#!/usr/bin/env python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requires=[
    'click',
    'pyyaml',
    'loguru',
    'tabulate',
    'unifi-api'
]

setuptools.setup(
    name='unificli',
    version='1.0.0',
    author='Joshua Schmidlkofer',
    author_email='joshland@gmail.com',
    description='API Ubiquity UniFi Controller',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/joshland/unificli.git',
    packages=setuptools.find_packages(),
    install_requires=requires
    dependency_links=[
        'https://github.com/joshland/unifi/tarball/master#egg=unifi-api-1.0.5'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Networking'
    ],
    entry_points="""\
    [console_scripts]
    eisnmap = unificli:cli
    """,
)
