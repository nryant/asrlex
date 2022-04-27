#!/usr/bin/env python
from setuptools import setup, find_packages

import versioneer

versioneer.versionfile_source = "asrlex/_version.py"
versioneer.versionfile_build = versioneer.versionfile_source
versioneer.tag_prefix = ""
versioneer.parentdir_prefix = "asrlex-"

setup(
    #Package.
    packages=['asrlex'],
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
    

