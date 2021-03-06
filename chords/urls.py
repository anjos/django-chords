#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Fri  8 Oct 08:32:00 2010

"""URLs for the chords project.
"""

from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

urlpatterns = patterns('chords.views',

    url(r'^$', RedirectView.as_view(url='song/'), name='index'),
    url(r'^pdf/$', 'view_songbook_pdf', name='view-songbook-pdf'),
    url(r'^artist/$', 'view_artists', name='view-artists'),
    url(r'^artist/(?P<artist_id>\d{1,4})/$', 'view_artist', name='view-artist'),
    url(r'^artist/(?P<artist_id>\d{1,4})/pdf/$', 'view_artist_songbook_pdf',
      name='view-artist-songbook-pdf'),
    url(r'^song/$', 'view_songs', name='view-songs'),
    url(r'^song/(?P<song_id>\d{1,4})/$', 'view_song', name='view-song'),
    url(r'^song/(?P<song_id>\d{1,4})/text/$', 'view_song_text',
      name='view-song-text'),
    url(r'^song/(?P<song_id>\d{1,4})/pdf/$', 'view_song_pdf',
      name='view-song-pdf'),
    url(r'^song/(?P<song_id>\d{1,4})/simple/$', 'view_song',
      {'template_name': 'chords/song_simple.html'},
      name='view-song-simple'),
    url(r'^translate/$', 'translate_song_text', name='translate-song-text'),
    url(r'^collection/$', 'view_collections', name='view-collections'),
    url(r'^collection/(?P<collection_id>\d{1,4})/$', 'view_collection', name='view-collection'),
    url(r'^collection/(?P<collection_id>\d{1,4})/pdf/$', 'view_collection_songbook_pdf',
      name='view-collection-songbook-pdf'),
  )

# use this instead of urlpatterns directly
namespaced = (urlpatterns, 'chords', 'chords')

