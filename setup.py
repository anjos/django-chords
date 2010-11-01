#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Created by Andre Anjos <andre.dos.anjos@cern.ch>
# Seg 14 Set 2009 14:42:06 CEST 

"""Installation instructions for django-chords
"""

from setuptools import setup, find_packages
        
setup(

    name = 'django-chords',
    version = '0.3.2',
    packages = find_packages(),

    # we also need all translation files and templates
    package_data = {
      'chords': [
        'templates/chords/*.html',
        'locale/*/LC_MESSAGES/*.po',
        'locale/*/LC_MESSAGES/*.mo',
        'media/css/*.css',
        'media/js/*.js',
        'media/img/*.jpg',
        'media/img/icons/16x16/*.png',
        ],
      },

    entry_points = {
      'django.scripts': [
        'chords_top2pro.py = chords.scripts.converter:top2chordpro',
        ]
      },

    zip_safe=False,

    install_requires = [
      'Django>=1.2',
      'docutils',
      'PIL',
      'reportlab',
      ],

    # metadata for upload to PyPI
    author = 'André Anjos',
    author_email = "andre.dos.anjos@gmail.com",
    description = 'Django extension to make your site hold chord-ed songs',
    license = "GPL v2 or superior",
    keywords = "django chords songs music",
    url = 'http://my.andreanjos.org/git/django-chords/',
)
