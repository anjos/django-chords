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
from django.conf import settings as djset
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required

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
  getreq = u''
  try: 
    order = request.GET.get('o', '-updated').strip()
    objects = objects.order_by(order)
    if request.GET.urlencode(): getreq = u'?%s' % request.GET.urlencode()
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
                              'getreq': getreq,
                            },
                            context_instance=RequestContext(request))


def view_songs(request, template_name="chords/songs.html"):
  """Views all songs input at the system, arranged by date. Lastest first."""
  
  objects = Song.objects.all()

  # A get request determines the order. The default is -updated
  getreq = u''
  try: 
    order = request.GET.get('o', '-updated').strip()
    objects = objects.order_by(order)
    if request.GET.urlencode(): getreq = u'?%s' % request.GET.urlencode()
  except FieldError:
    raise Http404

  paginator = Paginator(objects, objects.count())

  try: page = int(request.GET.get('page', '1'))
  except ValueError: page = 1

  try: pages = paginator.page(page)
  except (EmptyPage, InvalidPage): pages = paginator.page(paginator.num_pages)

  return render_to_response(template_name,
                            {
                              'pages': pages, 
                              'getreq': getreq,
                            },
                            context_instance=RequestContext(request))


def view_song(request, song_id, template_name="chords/song.html"):
  """Views a specific song."""
  
  return render_to_response(template_name,
                            {'object': Song.objects.get(id=song_id), },
                            context_instance=RequestContext(request))

def view_song_text(request, song_id):
  """Views a specific song chordpro representation."""
  o = Song.objects.get(id=song_id)
  response = HttpResponse(o.song, mimetype='text/plain')
  response['Content-Disposition'] = 'attachment; filename="%s.txt"' % \
      o.title.encode('ascii', 'ignore')
  return response 

def view_song_pdf(request, song_id):
  """Views a specific song PDF representation."""
  from pdf import pdf_set_locale, SongTemplate
  import locale
 
  o = Song.objects.get(id=song_id)

  # sets the locale so the dates and such get correctly printed
  old_locale = pdf_set_locale(request)

  response = HttpResponse(mimetype='application/pdf')
  response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % \
      o.title.encode('ascii', 'ignore')

  doc = SongTemplate(response)
  doc.author = o.user.get_full_name() + u'<' + o.user.email + u'>' 
  doc.title = o.title
  doc.subject = ugettext(u'Lyrics and Chords')

  story = o.pdf_story(doc)
  o.pdf_add_page_template(doc)

  doc.build(story)

  # restore default language
  locale.setlocale(locale.LC_ALL, old_locale)

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
  getreq = u''
  try: 
    order = request.GET.get('o', '-updated').strip()
    objects = objects.order_by(order)
    if request.GET.urlencode(): getreq = u'?%s' % request.GET.urlencode()
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
                              'getreq': getreq,
                            },
                            context_instance=RequestContext(request))


def view_songbook_pdf(request):
  """Returns a PDF book of all songs available in the website, in the requested
  order.   
  """
  from reportlab.platypus.tableofcontents import TableOfContents
  from reportlab.platypus import NextPageTemplate, PageBreak
  from pdf import SongBookTemplate, style, pdf_cover_page, pdf_set_locale
  import locale

  objects = Song.objects.all()

  # A get request determines the order. The default is -updated
  try: 
    order = request.GET.get('o', '-updated').strip()
    objects = objects.order_by(order)
  except FieldError:
    raise Http404

  # sets the locale so the dates and such get correctly printed
  old_locale = pdf_set_locale(request)

  response = HttpResponse(mimetype='application/pdf')
  response['Content-Disposition'] = 'attachment; filename="chordbook.pdf"'

  doc = SongBookTemplate(response)
  doc.author = djset.DEFAULT_FROM_EMAIL 
  doc.title = ugettext(u'Chordbook from %(site)s') % \
      {'site': Site.objects.get_current().name}
  doc.subject = ugettext(u'Lyrics and Chords Book')

  story = pdf_cover_page(objects, request)

  #appends and prepares table of contents
  story.append(NextPageTemplate('TOC'))
  story.append(PageBreak())
  story.append(TableOfContents())
  story[-1].levelStyles[0] = style['toc-entry']
  story[-1].dotsMinLevel = 0 #connecting dots

  #adds the lyrics
  objects = list(objects)
  for o in objects:
    o.pdf_add_page_template(doc)
    story.append(NextPageTemplate(o.pdf_template_id()))
    story.append(PageBreak())
    story += o.pdf_story(doc)

  #multi-pass builds are necessary to handle TOCs correctly
  doc.multiBuild(story)

  # restore default language
  locale.setlocale(locale.LC_ALL, old_locale)

  return response 

def view_artist_songbook_pdf(request, artist_id):
  """Returns a PDF book of all songs available in the website, in the requested
  order.   
  """
  from reportlab.platypus.tableofcontents import TableOfContents
  from reportlab.platypus import NextPageTemplate, PageBreak
  from pdf import SongBookTemplate, style, pdf_set_locale
  import locale

  artist = Artist.objects.get(id=artist_id)
  objects = Song.objects.filter(Q(composer=artist)|Q(performer=artist))

  # A get request determines the order. The default is -updated
  try: 
    order = request.GET.get('o', '-updated').strip()
    objects = objects.order_by(order)
  except FieldError:
    raise Http404

  # sets the locale so the dates and such get correctly printed
  old_locale = pdf_set_locale(request)

  response = HttpResponse(mimetype='application/pdf')
  response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % \
      artist.name.encode('ascii', 'ignore')

  doc = SongBookTemplate(response)
  doc.author = djset.DEFAULT_FROM_EMAIL 
  doc.title = artist.name
  doc.subject = ugettext(u'Lyrics and Chords Book')

  story = artist.pdf_cover_page(request)

  #appends and prepares table of contents
  story.append(NextPageTemplate('TOC'))
  story.append(PageBreak())
  story.append(TableOfContents())
  story[-1].levelStyles[0] = style['toc-entry']
  story[-1].dotsMinLevel = 0 #connecting dots

  #adds the lyrics
  objects = list(objects)
  for o in objects:
    o.pdf_add_page_template(doc)
    story.append(NextPageTemplate(o.pdf_template_id()))
    story.append(PageBreak())
    story += o.pdf_story(doc)

  #multi-pass builds are necessary to handle TOCs correctly
  doc.multiBuild(story)

  # restore default language
  locale.setlocale(locale.LC_ALL, old_locale)

  return response 

def view_collection_songbook_pdf(request, collection_id):
  """Returns a PDF book of all songs available in the website, in the requested
  order.   
  """
  from reportlab.platypus.tableofcontents import TableOfContents
  from reportlab.platypus import NextPageTemplate, PageBreak
  from pdf import SongBookTemplate, style, pdf_set_locale
  import locale

  collection = Collection.objects.get(id=collection_id)
  objects = collection.song.all()

  # A get request determines the order. The default is -updated
  try: 
    order = request.GET.get('o', '-updated').strip()
    objects = objects.order_by(order)
  except FieldError:
    raise Http404

  # sets the locale so the dates and such get correctly printed
  old_locale = pdf_set_locale(request)

  response = HttpResponse(mimetype='application/pdf')
  response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % \
      collection.name.encode('ascii', 'ignore')

  doc = SongBookTemplate(response)
  doc.author = collection.owner.get_full_name() + u'<' + \
      collection.owner.email + u'>' 
  doc.title = collection.name
  doc.subject = ugettext(u'Lyrics and Chords Book')

  story = collection.pdf_cover_page(request)

  #appends and prepares table of contents
  story.append(NextPageTemplate('TOC'))
  story.append(PageBreak())
  story.append(TableOfContents())
  story[-1].levelStyles[0] = style['toc-entry']
  story[-1].dotsMinLevel = 0 #connecting dots

  #adds the lyrics
  objects = list(objects)
  for o in objects:
    o.pdf_add_page_template(doc)
    story.append(NextPageTemplate(o.pdf_template_id()))
    story.append(PageBreak())
    story += o.pdf_story(doc)

  #multi-pass builds are necessary to handle TOCs correctly
  doc.multiBuild(story)

  # restore default language
  locale.setlocale(locale.LC_ALL, old_locale)

  return response 

@login_required
def translate_song_text(request):
  """This script does a top chord notation to chordpro notation of a POST
  request. It is meant to be used in a javascript POST request for automatic
  admin form update.
  """
  if not request.method == "POST": raise Http404
  if not request.POST.has_key('song'): raise Http404 
  from scripts.converter import convert
  converted = convert(request.POST['song'].split('\n'))
  response = HttpResponse(converted, mimetype='text/plain')
  response['Content-Disposition'] = 'attachment; filename="song.txt"'
  return response 
