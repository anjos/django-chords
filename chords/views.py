#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Fri  8 Oct 08:12:29 2010 

"""Some interesting views for the django-chors project
"""

from django.shortcuts import render_to_response#, redirect
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404, HttpResponse
from django.db.models.sql.query import FieldError
from django.db.models import Q

from models import *

def view_artists(request, template_name="chords/artists.html"):
  """Views all artists input at the system, arranged by name."""
  
  objects = Artist.objects.all()

  # A get request determines the order. The default is name 
  try: 
    order = request.GET.get('o', 'name').strip()
    objects = objects.order_by(order)
  except FieldError:
    raise Http404

  paginator = Paginator(objects, 20)

  try: page = int(request.GET.get('page', '1'))
  except ValueError: page = 1

  try: pages = paginator.page(page)
  except (EmptyPage, InvalidPage): pages = paginator.page(paginator.num_pages)

  return render_to_response(template_name,
                            {
                              'pages': pages, 
                            },
                            context_instance=RequestContext(request))

def view_artist(request, artist_id, template_name="chords/artist.html"):
  """Views all particularities from a certain artist."""

  artist = Artist.objects.get(id=artist_id)
  objects = Song.objects.filter(Q(composer=artist)|Q(performer=artist))

  # A get request determines the order. The default is -updated
  try: 
    order = request.GET.get('o', '-updated').strip()
    objects = objects.order_by(order)
  except FieldError:
    raise Http404

  paginator = Paginator(objects, 20)

  try: page = int(request.GET.get('page', '1'))
  except ValueError: page = 1

  try: pages = paginator.page(page)
  except (EmptyPage, InvalidPage): pages = paginator.page(paginator.num_pages)

  return render_to_response(template_name,
                            {
                              'object': artist,
                              'pages': pages, 
                            },
                            context_instance=RequestContext(request))


def view_songs(request, template_name="chords/songs.html"):
  """Views all songs input at the system, arranged by date. Lastest first."""
  
  objects = Song.objects.all()

  # A get request determines the order. The default is -updated
  try: 
    order = request.GET.get('o', '-updated').strip()
    objects = objects.order_by(order)
  except FieldError:
    raise Http404

  paginator = Paginator(objects, 20)

  try: page = int(request.GET.get('page', '1'))
  except ValueError: page = 1

  try: pages = paginator.page(page)
  except (EmptyPage, InvalidPage): pages = paginator.page(paginator.num_pages)

  return render_to_response(template_name,
                            {
                              'pages': pages, 
                            },
                            context_instance=RequestContext(request))


def view_song(request, song_id, template_name="chords/song.html"):
  """Views a specific song."""
  
  return render_to_response(template_name,
                            {'object': Song.objects.get(id=song_id), },
                            context_instance=RequestContext(request))

def view_song_text(request, song_id, template_name="chords/song.txt"):
  """Views a specific song chordpro representation."""
  o = Song.objects.get(id=song_id)
  response = HttpResponse(o.song, mimetype='text/plain')
  response['Content-Disposition'] = 'attachment; filename=%s.txt' % \
      o.title.encode('ascii', 'ignore')
  return response 

def view_collections(request, template_name="chords/collections.html"):
  """Views all collections input at the system, arranged by date. Lastest
  first."""

  objects = Collection.objects.all()

  # A get request determines the order. The default is -updated
  try: 
    order = request.GET.get('o', '-updated').strip()
    objects = objects.order_by(order)
  except FieldError:
    raise Http404

  paginator = Paginator(objects, 20)

  try: page = int(request.GET.get('page', '1'))
  except ValueError: page = 1

  try: pages = paginator.page(page)
  except (EmptyPage, InvalidPage): pages = paginator.page(paginator.num_pages)

  return render_to_response(template_name,
                            {'pages': pages, },
                            context_instance=RequestContext(request))

def view_collection(request, collection_id,
    template_name="chords/collection.html"):
  """Views a specific collection."""

  collection = Collection.objects.get(id=collection_id)
  objects = collection.song.all()

  # A get request determines the order. The default is -updated
  try: 
    order = request.GET.get('o', '-updated').strip()
    objects = objects.order_by(order)
  except FieldError:
    raise Http404

  paginator = Paginator(objects, 20)

  try: page = int(request.GET.get('page', '1'))
  except ValueError: page = 1

  try: pages = paginator.page(page)
  except (EmptyPage, InvalidPage): pages = paginator.page(paginator.num_pages)

  return render_to_response(template_name,
                            {
                              'object': collection,
                              'pages': pages, 
                            },
                            context_instance=RequestContext(request))


def songbook(request, by, index=True, order='descending'):
  """Returns a PDF book of all songs available in the website, in the requested
  order. Options for "by" are: performer (or composer, if performer is empty),
  when updated, when created. We sort in descending order unless stated
  otherwise.
  
  The PDF should contain an index if possible!
  """
  pass

