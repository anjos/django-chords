#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Fri  8 Oct 08:32:00 2010 

"""URLs for the chords project.
"""

from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

urlpatterns = patterns('chords.views',

    url(r'^$', 'index', name='index'), 
    url(r'^performer/$', 'by_performer', name='by-performer'), 
  )

# use this instead of urlpatterns directly
namespaced = (urlpatterns, 'chords', 'chords')

