#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Fri  8 Oct 08:12:29 2010 

"""Some interesting views for the django-chors project
"""

from django.shortcuts import render_to_response#, redirect
from django.template import RequestContext

def view_songs(request, template_name="chords/index.html"):
  """Views all songs input at the system, arranged by date. Lastest first."""

  return render_to_response(template_name,
                            context_instance=RequestContext(request))


def by_performer(request, template_name="chords/performer.html"):
  """View all songs by author or performer (if empty, by composer). Songs are
  arranged by the date they were entered in the system. Latest first."""

  return render_to_response(template_name,
                            context_instance=RequestContext(request))

def songbook(request, by, index=True, order='descending'):
  """Returns a PDF book of all songs available in the website, in the requested
  order. Options for "by" are: performer (or composer, if performer is empty),
  when updated, when created. We sort in descending order unless stated
  otherwise.
  
  The PDF should contain an index if possible!
  """
  pass

def performer_songbook(request, index=True, order='descending'):
  """Returns a PDF book of all songs available in the website for a certain
  performer or composer."""
  pass

def song(request, template_name="chords/song.html"):
  """Views a specific song."""
  
  return render_to_response(template_name,
                            context_instance=RequestContext(request))

