#!/usr/bin/env python
from setuptools import setup, find_packages

import versioneer

setup(
    #Package.
    namespace_packages=['asrlex'],
    packages=find_packages(),   # ???
    entry_points={'console_scripts' : ['asrlex=asrlex.cli:main',],},
    # TODO: Determine required versions.
    install_requires=['pybindgen',
                      'wurlitzer'],
    # Versioning.
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    # PyPI.
    name='asrlex',
    description=('A lightweight library for creating and manipulating '
                 'pronunciation lexicons for ASR.'),
    author='Neville Ryant',
    author_email='nryant@gmail.com')
    

