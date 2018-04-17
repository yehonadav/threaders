#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import re
from setuptools import setup

with io.open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

with io.open('threaders/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='threaders',
    version=version,
    url='https://github.com/yehonadav/threaders',
    license='Apache Software',
    author='Yehonadav Bar Elan',
    author_email='yonadav.barilan@gmail.com',
    maintainer='Yehonadav',
    maintainer_email='yonadav.barilan@gmail.com',
    description='A small module to support automation of generating valid python variable names from external data.',
    long_description=readme,
    packages=['threaders'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    extras_require={
        'dotenv': ['python-dotenv'],
        'dev': [
            'pytest>=3',
            'coverage',
            'tox',
            'sphinx',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points={
        'console_scripts': [
            'threaders = threaders.cli:main',
        ],
    },
)