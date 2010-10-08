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

from models import *
from parser import syntax_analysis, parse
import codecs

def count_collections(obj):
  return obj.collection_set.count()
count_collections.short_description = _(u'Collections')

class SongAdminForm(forms.ModelForm):
  class Meta:
    model = Song

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

admin.site.register(Collection, CollectionAdmin)
