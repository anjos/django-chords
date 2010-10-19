#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Fri 08 Oct 2010 14:18:40 CEST 

"""
"""

from django.contrib import admin
from django import forms
from django.utils.translation import *
from django.utils.translation import ugettext_lazy as _
from django.core.files.images import ImageFile

from models import *
from parser import syntax_analysis, parse
import codecs

class ArtistAdminForm(forms.ModelForm):
  class Meta:
    model = Artist

  def clean_avatar(self):
    if not self.cleaned_data["avatar"]: return self.cleaned_data["avatar"]
    try:
      f = ImageFile(self.cleaned_data["avatar"])
      if f.width != int(0.75 * f.height):
        raise forms.ValidationError, ugettext(u"Invalid avatar size (%(width)dx%(height)d). Avatars have to have a 3x4 (widthxheight) aspect ratio.") % {'width': f.width, 'height': f.height}
    except TypeError, e:
      raise forms.ValidationError, ugettext(u"Invalid avatar '%(filename)s'. Cannot be opened by Django.") % {'filename': self.cleaned_data["avatar"].name}
    return self.cleaned_data["avatar"]

def artist_image(self):
  return '<div style="text-align:center"><img src="%s" height="64" width="48" title="%s"/></div>' % \
      (self.image.url, self.name)
artist_image.short_description = _(u'Image')
artist_image.allow_tags = True

def count_songs(self):
  return '%d (%d)' % (self.performer.count(), self.composer.count())
count_songs.short_description = _(u'Songs')

def artist_color(self):
  return '<div style="color:#fff;background-color:#%(color)s;width:48;height:48;border:solid 1px black;text-align:center;vertical-align:center">%(color)s</div>' \
      % {'color': self.color}
artist_color.short_description = _(u'Color')
artist_color.allow_tags = True

class ArtistAdmin(admin.ModelAdmin):
  form = ArtistAdminForm
  list_display = ('name', artist_color, artist_image, count_songs)
  list_filter = ('color',)
  ordering = ('name', 'color',)
  list_per_page = 10
  search_fields = ['name', 'color',] 

admin.site.register(Artist, ArtistAdmin)

def count_collections(self):
  return self.collection_set.count()
count_collections.short_description = _(u'Collections')

class SongAdminForm(forms.ModelForm):
  class Meta:
    model = Song
    widgets = {
        'song': forms.Textarea(attrs={'class': 'song-field-admin', 'wrap': 'off'}),
        }

  class Media:
    css = {
        'screen': ('chords/css/admin.css',)
        }
    
  def clean_song(self):
    try:
      syntax_analysis(parse(self.cleaned_data["song"]))
    except SyntaxError, e:
      raise forms.ValidationError, ugettext(u"Invalid file syntax. Either choose another file or fix the one you are trying to upload. Here is a hint: %(error)s") % {'error': e}
    return self.cleaned_data["song"]
    
class SongAdmin(admin.ModelAdmin):
  form = SongAdminForm
  list_display = ('title', 'performer', 'composer', 'year', 'tone', 'user', 'date', 'updated', count_collections)
  list_filter = ('year', 'tone', 'user', 'date', 'updated')
  ordering = ('-updated', 'title',)
  list_per_page = 20
  search_fields = ['title', 'performer', 'composer', 'year', 'tone', 'user']
  save_on_top = True

admin.site.register(Song, SongAdmin)

def count_songs(obj):
  return obj.song.count()
count_songs.short_description = _(u'Songs')

class CollectionAdmin(admin.ModelAdmin):
  list_display = ('name', 'owner', 'date', 'updated', count_songs)
  list_filter = ('owner', 'date', 'updated')
  ordering = ('-updated', 'name', 'owner')
  list_per_page = 20
  search_fields = ['name',]
  filter_horizontal = ('song',)

admin.site.register(Collection, CollectionAdmin)
