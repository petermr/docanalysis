#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import configparser
import os

with open('README.md') as readme_file:
    readme = readme_file.read()
requirements = ['pandas', 'spacy', 'numpy',
                'matplotlib', 'tqdm', 'en_core_web_sm', 'beautifulsoup4']

setup(
    name='docanalysis',
    version="0.0.2",
    description='extract structured information from ethics paragraphs',
    long_description=readme,
    author='Ayush Garg, Shweata N. Hegde',
    author_email='ayush@science.org.in',
    url='https://github.com/petermr/docanalysis',
    packages=[
        'extract_entities',
    ],
    package_dir={'extract_entities':
                 'docanalysis'},
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
