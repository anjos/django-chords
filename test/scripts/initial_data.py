#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Created by Andre Anjos <andre.dos.anjos@cern.ch>
# Sex 05 Mar 2010 11:48:41 CET 

"""Creates repositories for the inital tests.
"""

from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.core.files import File
from chords.models import *
import os, sys, fnmatch

from django.contrib.auth.models import User

def main():
  # This bit will create the superuser
  User.objects.all().delete()

  name = 'admin'
  admin = User()
  admin.username = name
  admin.first_name = name.capitalize()
  admin.last_name = name.capitalize() + 'ston'
  admin.email = '%s@example.com' % name
  admin.is_staff = True
  admin.is_active = True
  admin.is_superuser = True
  admin.set_password(admin.username)
  admin.save()
  print 'Created user "%s" with password "%s"' % (name, name)

  # This bit will create a default artist
  Artist.objects.all().delete()
  unknown = Artist()
  unknown.name = u'Desconhecido da Conceição'
  unknown.color = '000'
  unknown.save()
  print 'Created %s' % unknown

  # This bit will load our chord examples
  Song.objects.all().delete()
  counter = 0
  for repeat in range(10):
    for ex in fnmatch.filter(os.listdir('examples'), '*.chord'):
      f = open(os.path.join('examples', ex), 'rt')
      s = Song()
      s.user = admin
      counter += 1
      s.title = 'Song %d' % counter
      s.performer = unknown 
      s.composer = unknown
      s.year = 2010
      s.tone = 'A'
      s.song = f.read()
      s.save()
      f.close()
      print 'Created %s' % s

  # This bit will create 2 collections
  Collection.objects.all().delete()
  c1 = Collection()
  c1.name = 'First Collection'
  c1.owner = admin
  c1.save()
  c1.song = Song.objects.all()[:3]
  c1.save()
  print 'Created %s' % c1
  c2 = Collection()
  c2.name = 'Second Collection'
  c2.owner = admin
  c2.save()
  c2.song = Song.objects.all()[3:]
  c2.save()
  print 'Created %s' % c2
