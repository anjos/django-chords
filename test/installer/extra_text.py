#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Created by Andre Anjos <andre.dos.anjos@cern.ch>
# Sun 28 Feb 19:52:16 2010 

"""A bunch of methods that will be added to the boostrap script. Please refer
to the virtualenv homepage for the explanation on those.
"""

import os, sys, subprocess

# Where to find software
SWURL = [
    'http://sw.andreanjos.org/git/simple/',
    'file://' + os.path.join(os.path.realpath(os.curdir), 'downloads'),
    ]

PACKAGES = [
    ]
SOURCES = [
    #('git+http://github.com/simonw/django-openid.git', 'django-openid'),
    ]
LOCALS = [
    '..',
    '.',
    ]

def after_install(options, home_dir):
  """After everything is installed, this function is called.
  
  At this point, we populate our environment with all our goods.
  """
  if sys.platform == 'win32': bin = 'Scripts'
  else: bin = 'bin'

  # we first install pip, which is easier to use
  installer = [os.path.join(home_dir, bin, 'easy_install'), '--quiet']
  subprocess.call(installer + ['pip'])
  
  installer = [os.path.join(home_dir, bin, 'pip'), 'install']
  installer += ['--use-mirrors']
  installer += ['--find-links=%s' % (k,) for k in SWURL]
  if options.upgrade: installer.append('--upgrade')

  installer += PACKAGES 
  installer += ['--editable=%s#egg=%s' % (k,k) for k in SOURCES]
  installer += ['--editable='+k for k in LOCALS]

  subprocess.call(installer)

def extend_parser(parser):
  """Adds an upgrade option."""
  parser.add_option('-U', '--upgrade', action='store_true', dest='upgrade', 
    help='Use this if you want to upgrade instead of installing (default)')
