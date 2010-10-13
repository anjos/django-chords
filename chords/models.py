#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 04 Oct 2010 15:05:04 CEST 

"""Models for chords.
"""

import os, datetime, hashlib, re
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext, ugettext
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.images import ImageFile

from parser import syntax_analysis, parse

def media(path):
  return os.path.join(settings.MEDIA_ROOT, path)

SPACE = re.compile(r'\s+')
def strname(v): return SPACE.sub('', v.encode('ascii', 'ignore'))

class Artist(models.Model):
  """Defines an artist, a person that performs or composes songs."""

  def upload_path(self, filename):
    extension = os.path.splitext(filename)[1]
    path = os.path.join('chords', 'artists', 'images')
    if not os.path.exists(media(path)): os.makedirs(media(path))
    path += strname(self.name) + extension.lower()
    if os.path.exists(media(path)): unlink(media(path))
    return path

  name = models.CharField(_(u'Name'), help_text=_(u'You can write here the name of the artist.'), max_length=100, blank=False, null=False, unique=True)

  color = models.CharField(_(u'Color'), max_length=3, help_text=_(u'The hexadecimal 3-digit color representation of this artist in the RGB format. Example: #fff for white, #000 for black or #f00 for pure red. Omit the "#" (hash mark) when you specify the color.'), null=False, blank=False)
  
  avatar = models.ImageField(_('Avatar'), upload_to=upload_path, help_text=_('Specify here the file that will be uploaded. This file should be a photo of the artist. The image has to be a portrait of 3x4 in one of the web-supported formats like JPEG or PNG.'), null=True, blank=True)

  def _image(self):
    """Returns the current avatar or the "unknown.jpg" stock image."""
    if self.avatar: return self.avatar

    path = os.path.join('chords', 'img', 'unknown.jpg')
    f = ImageFile(open(media(path), 'rb'))
    f.url = os.path.join(settings.MEDIA_URL, path) 
    return f

  image = property(_image)
  
  class Meta:
    verbose_name = _(u"artist")
    verbose_name_plural = _(u"artists")

  def __unicode__(self):
    return self.name

class Song(models.Model):
  """A song with chords."""

  TONE_CHOICES = (
      (u'A', _(u'A')),
      (u'A#', _(u'A sharp')),
      (u'Bb', _(u'B flat')),
      (u'B', _(u'B')),
      (u'C', _(u'C')),
      (u'C#', _(u'C sharp')),
      (u'Db', _(u'D flat')),
      (u'D', _(u'D')),
      (u'D#', _(u'D sharp')),
      (u'Eb', _(u'E flat')),
      (u'E', _(u'E')),
      (u'F', _(u'F')),
      (u'F#', _(u'F sharp')),
      (u'Gb', _(u'G flat')),
      (u'G', _(u'G')),
      (u'G#', _(u'G sharp')),
      (u'Ab', _(u'A flat')),
      (u'Am', _(u'A minor')),
      (u'A#m', _(u'A sharp minor')),
      (u'Bbm', _(u'B flat minor')),
      (u'Bm', _(u'B minor')),
      (u'Cm', _(u'C minor')),
      (u'C#m', _(u'C sharp minor')),
      (u'Dbm', _(u'D flat minor')),
      (u'Dm', _(u'D minor')),
      (u'D#m', _(u'D sharp minor')),
      (u'Ebm', _(u'E flat minor')),
      (u'Em', _(u'E minor')),
      (u'Fm', _(u'F minor')),
      (u'F#m', _(u'F sharp minor')),
      (u'Gbm', _(u'G flat minor')),
      (u'Gm', _(u'G minor')),
      (u'G#m', _(u'G sharp minor')),
      (u'Abm', _(u'A flat minor')),
      )

  user = models.ForeignKey(User, null=False)

  date = models.DateTimeField(_('Created'), 
      auto_now_add=True, editable=False, null=False, blank=False)

  updated = models.DateTimeField(_('Last updated'), 
      auto_now=True, editable=False, null=False, blank=False)

  title = models.CharField(_(u'Title'), max_length=100, help_text=_(u'This song\'s title'), blank=False, null=False)

  performer = models.ForeignKey(Artist, related_name='performer', null=False)

  composer = models.ForeignKey(Artist, related_name='composer', null=False)

  year = models.PositiveSmallIntegerField(_(u'Year'), help_text=_(u'The year of the composition or performance. You may leave this field blank if you do not know it.'), blank=True, null=True)

  tone = models.CharField(_(u'Tone'), help_text=_(u'The tone for this music'),
      max_length=3, choices=TONE_CHOICES, blank=False, null=False)

  song = models.TextField(_(u'Song'), max_length=12000, help_text=_(u'Put here the text lines describing this song. We use the "chordpro" textual format. Read the project documentation for more information on the format.'), null=False, blank=False)

  def save(self, *args, **kwargs):
    syntax_analysis(parse(self.song)) #throws if any problems occur
    super(Song, self).save(*args, **kwargs)

  class Meta:
    verbose_name = _(u"song")
    verbose_name_plural = _(u"songs")

    # please note that if you change the field bellow, you should revise 
    # upload_path() above, to make sure we hold uniqueness for file names.
    unique_together = ('title', 'tone', 'performer', 'composer')

  def __unicode__(self):
    return ugettext(u'Song(%(title)s in %(tone)s)') % \
        {'title': self.title, 'tone': self.get_tone_display()}

  def items(self):
    return syntax_analysis(parse(self.song))

  def by(self):
    """Returns a nice arrangement for performer/composer"""
    if self.performer == self.composer: return self.performer.name
    return u'%s (%s)' % (self.performer.name, self.composer.name)

class Collection(models.Model):
  """A collection of songs."""

  name = models.CharField(_(u'Name'), max_length=100, help_text=_(u'The name of this collection'), blank=False, null=False, unique=True)

  date = models.DateTimeField(_('Created'), 
      auto_now_add=True, editable=False, null=False, blank=False)

  updated = models.DateTimeField(_('Last updated'),
      auto_now=True, editable=False, null=False, blank=False)

  owner = models.ForeignKey(User, null=False)

  song = models.ManyToManyField(Song)

  class Meta:
    verbose_name = _(u"collection")
    verbose_name_plural = _(u"collections")

  def __unicode__(self):
    return ungettext(u'Collection(%(name)s from %(owner)s, %(songs)d song)', 
                     u'Collection(%(name)s from %(owner)s, %(songs)d songs)', 
                     self.song.count()) % \
                         {
                           'name': self.name, 
                           'songs': self.song.count(), 
                           'owner': self.owner.username
                         }

  def last_update(self):
    """Returns the last updated song on this collection."""
    return self.song.order_by('-updated')[0]
