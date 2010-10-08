#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 04 Oct 2010 15:05:04 CEST 

"""Models for chords.
"""

import os, datetime, hashlib
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext, ugettext
from django.contrib.auth.models import User
from django.conf import settings

from parser import syntax_analysis, parse

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

  performer = models.CharField(_(u'Performer'), help_text=_(u'You can write here the name of the performer you took this version from.'), max_length=100, blank=True)

  composer = models.CharField(_(u'Composer'), help_text=_(u'The original composer of this song'), max_length=100, blank=True)

  year = models.PositiveSmallIntegerField(_(u'Year'), help_text=_(u'The year of composition.'), blank=True, null=True)

  tone = models.CharField(_(u'Tone'), help_text=_(u'The tone for this music'),
      max_length=3, choices=TONE_CHOICES, blank=False, null=False)

  def upload_path(self, original):
    """Tells the FileField how to choose a name for this file."""
    hashable = self.title + self.performer + self.composer + self.tone
    sha1 = hashlib.sha1(hashable.encode('ascii','ignore')).hexdigest()[:8]
    path = os.path.join('chords', 'songs', sha1 + '.chord')
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, path)):
      os.unlink(os.path.join(settings.MEDIA_ROOT, path))
    return path

  song = models.FileField(_(u'Song'), help_text=_(u'Upload the text file containing your song using this field. We use the "chordpro" textual format. Read the project documentation for more information on the format.'), null=False, blank=False, upload_to=upload_path)

  def save(self, *args, **kwargs):
    self.song.open('rt')
    syntax_analysis(parse(self.song.file)) #throws if any problems occur
    self.song.seek(0)
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

