#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 04 Oct 2010 15:05:04 CEST

# A note on strftime: for PDF/unicode handling always decode the output of
# that function with .decode('latin-1') or TypeErrors may occur.

"""Models for chords.
"""

import os, datetime, hashlib, re
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext, ugettext
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.images import ImageFile
from django.core.urlresolvers import reverse

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
    path += os.sep + strname(self.name) + extension.lower()
    if os.path.exists(media(path)): unlink(media(path))
    return path

  name = models.CharField(_(u'Name'), help_text=_(u'You can write here the name of the artist.'), max_length=100, blank=False, null=False, unique=True)

  color = models.CharField(_(u'Color'), max_length=3, help_text=_(u'The hexadecimal 3-digit color representation of this artist in the RGB format. Example: #fff for white, #000 for black or #f00 for pure red. Omit the "#" (hash mark) when you specify the color.'), null=False, blank=False)

  avatar = models.ImageField(_('Avatar'), upload_to=upload_path, help_text=_('Specify here the file that will be uploaded. This file should be a photo of the artist. The image has to be a portrait of 3x4 in one of the web-supported formats like JPEG or PNG.'), null=True, blank=True)

  def _image(self):
    """Returns the current avatar or the "unknown.jpg" stock image."""
    if self.avatar: return self.avatar

    path = os.path.join('chords', 'img', 'unknown.jpg')
    f = ImageFile(open(os.path.join(settings.STATIC_ROOT, path), 'rb'))
    f.url = os.path.join(settings.STATIC_URL, path)
    return f

  image = property(_image)

  def pdf_color(self):
   """Returns the equivalent reportlab Color object from the artist color."""

   from reportlab.lib.colors import Color
   red = int(self.color[0], 16)/16.0
   if red < 0: red = 0
   elif red > 1: red = 1
   green = int(self.color[1], 16)/16.0
   if green < 0: green = 0
   elif green > 1: green = 1
   blue = int(self.color[2], 16)/16.0
   if blue < 0: blue = 0
   elif blue > 1: blue = 1
   return Color(red, green, blue, 1)

  class Meta:
    verbose_name = _(u"artist")
    verbose_name_plural = _(u"artists")

  def __unicode__(self):
    return self.name

  def last_update(self):
    """Returns the last updated song or this artist."""
    as_performer = self.performer.order_by('-updated')
    as_composer = self.composer.order_by('-updated')
    if not as_performer.count() and as_composer.count():
      return as_composer[0]
    elif not as_composer.count() and as_performer.count():
      return as_performer[0]
    elif as_composer.count() and as_performer.count():
      if as_composer[0].updated < as_performer[0].updated:
        return as_performer[0]
      else:
        return as_composer[0]
    return None

  def pdf_cover_page(self, request):
    """Bootstraps our PDF sequence of flowables."""
    from pdf import style
    from reportlab.platypus import Paragraph, Spacer, PageBreak
    from reportlab.lib.units import cm
    from time import strftime

    story = []
    story.append(Paragraph(ugettext(u'<i>Chordbook</i><br/><b>%(name)s</b>') % \
        {'name': self.name}, style['cover-title']))
    story.append(Spacer(1, 3*cm))
    update_date = self.last_update()
    if not update_date: update_date = u''
    else: update_date = strftime('%a, %d/%b/%Y', self.last_update().updated.timetuple()).decode('latin-1')
    story.append(Paragraph(ugettext(u'Last update: <b>%(update)s</b><br/>%(url)s<br/>Downloaded on %(date)s') % \
        {
         'update': update_date,
         'url': request.build_absolute_uri(),
         'date': strftime('%a, %d/%b/%Y').decode('latin-1'),
        },
        style['cover-subtitle']))
    return story

  def get_absolute_url(self):
    return reverse('chords:view-artist', kwargs={'artist_id': self.id})

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

  two_columns = models.BooleanField(_(u'Two columns'), help_text=_(u'This field determines how printed output (PDFs) will be arranged. If you left it clicked, PDF output will be arranged in two columns. Take attention to the width of the song text in this case, to avoid overflowing or broken paragraphs. You have approximately 40 columns per frame in this case.'), default=False)

  song = models.TextField(_(u'Song'), max_length=12000, help_text=ugettext(u'Put here the text lines describing this song. We use the "chordpro" textual format (<a href="%(url)s">reference here</a>). Read the project documentation for more information on the format.') % {'url': 'http://www.pmwiki.org/wiki/Cookbook/ChordPro-Format'}, null=False, blank=False)

  def save(self, *args, **kwargs):
    syntax_analysis(parse(self.song)) #throws if any problems occur
    super(Song, self).save(*args, **kwargs)

  class Meta:
    verbose_name = _(u"song")
    verbose_name_plural = _(u"songs")
    unique_together = ('title', 'tone', 'performer', 'composer')

  def __unicode__(self):
    return ugettext(u'%(title)s in %(tone)s (%(performer)s)') % \
        {
         'title': self.title,
         'tone': self.get_tone_display(),
         'performer': self.performer.name
        }

  def items(self):
    return syntax_analysis(parse(self.song))

  def items_by_column(self):
    i = self.items()
    if len(i) <= 1: return i
    #else, we can split it better
    cut = len(i)/2
    if len(i)%2 == 1:
      #if the number of elements is odd, put more on the first column
      cut += 1
    return (i[:cut], i[cut:])

  def by(self):
    """Returns a nice arrangement for performer/composer"""
    if self.performer == self.composer: return self.performer.name
    return u'%s (%s)' % (self.performer.name, self.composer.name)

  def pdf_basic_page(self, canvas, doc):
    """Sets elements that are common to all song PDF pages in django-chords."""

    from reportlab.lib.colors import Color
    from reportlab.lib.units import cm
    from time import strftime

    # draws the rectangle with the performer name and picture
    # remember: coordinates (0,0) start at bottom left and go up and to the
    # right!
    canvas.setFillColor(self.performer.pdf_color())
    page_height = doc.bottomMargin + doc.height + doc.topMargin
    page_width = doc.leftMargin + doc.width + doc.rightMargin
    y = page_height - doc.topMargin + 0.2*cm # a bit above the top margin
    rect_height = page_height - y
    canvas.rect(0, y, page_width, rect_height, fill=True, stroke=False)

    image = self.performer.image
    image_height = 100
    image_width = (image_height/float(image.height)) * image.width
    padding = 0.5*cm
    image_x = page_width - image_width - padding
    image_y = page_height - padding - image_height
    border = 4
    canvas.setFillGray(1)
    canvas.setStrokeGray(0.8)
    canvas.roundRect(image_x-border, image_y-border, image_width + (2*border),
        image_height + (2*border), radius=border/2, fill=True, stroke=True)
    canvas.drawImage(media(image.name), image_x, image_y, width=image_width,
        height=image_height, mask=None)

    name = canvas.beginText()
    name.setTextOrigin(doc.leftMargin, y+0.4*cm)
    name.setFont('Times-Roman', 20)
    name.setFillGray(1)
    name.textLine(self.performer.name)
    canvas.drawText(name)

    revision = canvas.beginText()
    revision.setTextOrigin(doc.leftMargin, doc.bottomMargin-(0.1*cm))
    revision.setFont('Times-Italic', 9)
    revision.setFillColor(Color(0, 0.4, 0, 1))
    revision.textLine(ugettext(u'%(who)s on %(when)s') % \
        {'who': self.user.first_name.capitalize(),
         'when': strftime('%a, %d/%b/%Y', self.updated.timetuple()).decode('latin-1')}
        )
    canvas.drawText(revision)

    # draws a line between the columns if we are in two column mode
    if self.two_columns:
      start_pad = 1.5*cm
      canvas.setStrokeColor(self.performer.pdf_color())
      canvas.setLineWidth(0.1*cm)
      canvas.setStrokeAlpha(0.5)
      canvas.setLineCap(1) #round ends
      canvas.line(page_width/2, doc.bottomMargin+start_pad,
          page_width/2, image_y-border-start_pad)

  def pdf_template_id(self):
    return 'SongTemplate-%d'  % self.id

  def pdf_add_page_template(self, doc):
    """Adds my own page template to the document."""
    from reportlab.lib.units import cm
    from reportlab.platypus.frames import Frame
    from reportlab.platypus.doctemplate import PageTemplate

    doc._calc() #taken from reportlab source code (magic)

    # The switch between one or two columns PDF output reflects on having one
    # or two frames. If we have two frames, the width and the start position
    # of each frame has to be computed slightly differently.
    #
    # Special attention to the right frame or its start will meet the picture
    # of the artist. So, we start about 2 cm down.
    if self.two_columns:
      padding = 0.5 * cm;
      frame_width = (doc.width - padding) / 2
      frames = [
          Frame(doc.leftMargin, doc.bottomMargin, frame_width, doc.height,
            id='column-1', leftPadding=0, rightPadding=0),
          Frame(doc.leftMargin + frame_width + padding, doc.bottomMargin,
            frame_width, doc.height - 2 * cm,
            id='column-2', leftPadding=0, rightPadding=0),
          ]
    else:
      frames = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
          id='normal', leftPadding=0, rightPadding=0)

    template = [PageTemplate(id='FirstPageSongTemplate', frames=frames,
      onPage=self.pdf_page_template_first, pagesize=doc.pagesize)]
    template = [PageTemplate(id=self.pdf_template_id(), frames=frames,
      onPage=self.pdf_page_template, pagesize=doc.pagesize)]
    doc.addPageTemplates(template)

  def pdf_page_template_first(self, canvas, doc):
    """If the song is printed alone, the first page is special."""

    canvas.saveState()
    self.pdf_basic_page(canvas, doc)
    canvas.restoreState()

  def pdf_page_template(self, canvas, doc):
    """Creates a personalized PDF page view for this song."""

    from reportlab.lib.units import cm
    from pdf import page_circle_center

    canvas.saveState()

    self.pdf_basic_page(canvas, doc)

    # Draws song name and page number
    title = canvas.beginText()
    title.setTextOrigin(doc.leftMargin + doc.width/2, doc.bottomMargin-(0.1*cm))
    title.setFont('Times-Roman', 9)
    title.setFillGray(0.2)
    title.textLine(u"%s" % (self.title))
    page_x = doc.width+doc.rightMargin+0.2*cm
    page_y = doc.bottomMargin-(0.1*cm)
    page_fontsize = 11
    page = canvas.beginText()
    page.setTextOrigin(page_x, page_y)
    page.setFont('Helvetica-Bold', page_fontsize)
    page.setFillGray(1)
    page_number = doc.page
    page.textLine('%d' % page_number)

    #circle around number
    canvas.setFillColor(self.performer.pdf_color())
    circle_x, circle_y = page_circle_center(page_x, page_y,
        page_fontsize, page_number)
    canvas.circle(circle_x, circle_y, 1.5*page_fontsize, fill=True,
        stroke=False)

    canvas.drawText(title)
    canvas.drawText(page)

    canvas.restoreState()

  def pdf_story(self, doc):
    """Writes itself as a PDF story."""

    from pdf import Spacer, Paragraph, style, fontsize, tide, colwidth

    # what is the maximum width of text?
    if self.two_columns: width = colwidth['double']
    else: width = colwidth['single']

    story = [Paragraph(self.title, style['song-title'])]
    story.append(Paragraph(ugettext(u'Tone') + ': ' + self.get_tone_display(),
      style['tone']))
    story.append(Spacer(1, fontsize))
    story += [k.as_flowable(width) for k in self.items()]
    story = [k for k in story if k]

    return tide(story, doc)

  def get_absolute_url(self):
    return reverse('chords:view-song', kwargs={'song_id': self.id})

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
    songs = self.song.order_by('-updated')
    if not songs.count(): return None
    return songs[0]

  def pdf_cover_page(self, request):
    """Bootstraps our PDF sequence of flowables."""
    from pdf import style
    from reportlab.platypus import Paragraph, Spacer, PageBreak
    from reportlab.lib.units import cm
    from time import strftime

    story = []
    story.append(Paragraph(ugettext(u'<i>Chordbook</i><br/><b>%(name)s</b>') % \
        {'name': self.name}, style['cover-title']))
    story.append(Spacer(1, 3*cm))
    update_date = self.last_update().updated
    if not update_date: update_date = self.updated
    story.append(Paragraph(ugettext(u'<i>%(name)s</i>, last update: <b>%(update)s</b><br/>%(url)s<br/>Downloaded on %(date)s') % \
        {
         'name': self.owner.get_full_name(),
         'update': strftime('%a, %d/%b/%Y', update_date.timetuple()).decode('latin-1'),
         'url': request.build_absolute_uri(),
         'date': strftime('%a, %d/%b/%Y').decode('latin-1'),
        },
        style['cover-subtitle']))
    return story

  def get_absolute_url(self):
    return reverse('chords:view-collection', kwargs={'collection_id': self.id})

