#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import configparser
import os
with open(os.path.join(os.path.dirname(__file__), "ethics_statement", "config.ini")) as f:
    config_file = f.read()
config = configparser.RawConfigParser(allow_no_value=True)
config.read_string(config_file)
version = config.get("ethics_statement", "version")

with open('README.md') as readme_file:
    readme = readme_file.read()
requirements = ['pandas', 'spacy', 'numpy',
            'matplotlib','tqdm','en_core_web_sm','BeautifulSoup','xml.etree.ElementTree']

setup(
    name='ethics_statement',
    version=f"{version}",
    description='extract structured information from ethics paragraphs',
    long_description=readme,
    author='Ayush Garg, Shweata N. Hegde',
    author_email='ayush@science.org.in',
    url='https://github.com/petermr/docanalysis',
    packages=[
        'ethics_statement',
    ],
    package_dir={'ethics_statement':
                 'ethics_statement_generic'},
    include_package_data=True,
    install_requires=requirements,
    license='Apache License',
    zip_safe=False,
    keywords='research automation',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',

    ],
)
