#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 04 Oct 2010 15:05:04 CEST 

"""Models for chords.
"""

import os, datetime, hashlib
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

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

  user = models.ForeignKey(User, null=False, default=User.objects.get(id=1))

  date = models.DateTimeField(_('Created'), 
      auto_now_add=True, editable=False, null=False, blank=False)

  updated = models.DateTimeField(_('Last updated'), 
      auto_now=True, editable=False, null=False, blank=False)

  title = models.CharField(_(u'Title'), max_length=100, help_text=_(u'This song\'s title'), blank=False, null=False)

  performer = models.CharField(_(u'Performer'), help_text=_(u'You can write here the name of the performer you took this version from.'), max_length=100, blank=True)

  composer = models.CharField(_(u'Composer'), help_text=_(u'The original composer of this song'), max_length=100, blank=True)

  year = models.PositiveSmallIntegerField(_(u'Year'), help_text=_(u'The year of composition.'), blank=True)

  tone = models.CharField(_(u'Tone'), help_text=_(u'The tone for this music'),
      max_length=3, choices=TONE_CHOICES, blank=False, null=False)

  def upload_path(object, original):
    """Tells the FileField how to choose a name for this file."""
    f = open(original, 'rt')
    sha1 = hashlib.sha1(f.read()).hexdigest()[:8]
    f.close()
    return os.path.join('chords', sha1 + '.chord')

  song = models.FileField(_(u'Song'), help_text=_(u'Upload the text file containing your song using this field. We use the "chordpro" textual format. Read the project documentation for more information on the format.', null=False, blank=False, upload_to=upload_path)
