#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Fri 01 Oct 2010 12:07:59 CEST 

"""Project setup.
"""

from setuptools import setup, find_packages
from djsetup import develop

setup(

    name = "chords-test",
    version = "1.0",
    packages = find_packages(),

    # we also need all translation files and templates
    package_data = {
      'test': [
        ],
      },

    entry_points = {
      'console_scripts': [
        'djm = scripts.manage:main',
        ],
      'django.settings': [
        'settings = settings',
        ],
      'django.scripts': [
        'start_project.py = scripts.initial_data:main',
        'pdf.py = scripts.pdftest:main',
        ],
      },

    # replaces the "develop" target with my own, that extends it.
    cmdclass = {
      'develop': develop,
      },

    zip_safe=False,

    install_requires = [
        'django-chords',
        'django-rosetta',
      ],

    # metadata for upload to PyPI
    author = "Andre Anjos",
    author_email = "andre.anjos@idiap.ch",
    description = "Provides a test framework",
    license = "PSF",
    keywords = "django test",
    url = "",   # project home page, if any

)
