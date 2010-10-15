#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Wed 13 Oct 14:10:19 2010 

"""PDF generation for chords.
"""

# the pdf generation stuff
from reportlab.platypus import Paragraph, XPreformatted, Spacer, CondPageBreak
from reportlab.platypus.flowables import NullDraw
from reportlab.platypus import NextPageTemplate
from reportlab.platypus import BaseDocTemplate
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT 

from django.contrib.sites.models import Site
from django.utils.translation import ungettext, ugettext

style = {}

fontsize = 9 #points

style['normal'] = ParagraphStyle(name='normal', 
                                 fontName='Times-Roman',
                                 fontSize=fontsize,
                                 leading=int(1.3 * fontsize),
                                 leftIndent=0,
                                 allowWidows=0,
                                 allowOrphans=0)

style['cover-title'] = ParagraphStyle(name='cover-title', 
                                parent=style['normal'],
                                fontSize=3 * fontsize,
                                alignment=TA_CENTER,
                                leading=int(3.6 * fontsize))

style['cover-subtitle'] = ParagraphStyle(name='cover-subtitle', 
                                         parent=style['normal'],
                                         fontSize=1.8 * fontsize,
                                         textColor = Color(0.3, 0.3, 0.3, 1),
                                         alignment=TA_CENTER,
                                         leading=int(3.6 * fontsize))

style['toc-entry'] = ParagraphStyle(name='toc-entry', 
                                    parent=style['normal'],
                                    fontSize=1.5 * fontsize,
                                    textColor = Color(0.3, 0.3, 0.3, 1),
                                    leading=int(1.8 * fontsize))

style['song-title'] = ParagraphStyle(name='song-title', 
                                parent=style['normal'],
                                fontSize=2 * fontsize,
                                leading=int(2.6 * fontsize))

style['tone'] = ParagraphStyle(name='tone',
                               parent=style['normal'],
                               fontName='Times-Italic',
                               font = int(1.5 * fontsize),
                               leading = int(1.7 * fontsize))

style['verse'] = ParagraphStyle(name='verse',
                                 parent=style['normal'],
                                 fontName='Courier')

style['tablature'] = ParagraphStyle(name='tablature',
                                    parent=style['verse'],
                                    textColor = Color(0, 0.67, 0, 1),
                                    fontName='Courier-Bold',
                                    spaceBefore = fontsize,
                                    spaceAfter = fontsize)

style['chorus'] = ParagraphStyle(name='chorus',
                                 parent=style['verse'],
                                 textColor = Color(0.67, 0, 0, 1),
                                 fontName = 'Courier-Bold',
                                 spaceBefore = fontsize,
                                 spaceAfter = fontsize)

style['comment'] = ParagraphStyle(name='comment',
                                  parent=style['verse'],
                                  textColor = Color(0.67, 0.67, 0.67, 1),
                                  fontName = 'Courier-Oblique')

def tide(story, doc):
  """This method will pre-calculate the size of the following flowable and
  force a page break on the story if the space available is not enough to
  contain the flowable. This avoids the break-up verses, choruses and
  tablatures."""

  retval = []
  frame_width = doc.width - doc.leftMargin - doc.rightMargin
  frame_height = doc.height - doc.topMargin - doc.bottomMargin
  for k in story:
    if not retval: 
      retval.append(k)
      continue

    width, height = k.wrap(frame_width, frame_height)
    retval.append(CondPageBreak(height))
    retval.append(k)

  return retval

def page_circle_center(x, y, fontsize, value):
  """Calculates the approximate circle center given the page positioning,
  fontsize and its current value."""
  length = len(str(value)) #the field length

  if length == 1: #only one digit in the page
    return x+0.25*fontsize, y+0.35*fontsize
  elif length == 2: #two digits in the page
    return x+0.5*fontsize, y+0.35*fontsize
  elif length == 3: #three digits
    return x+0.75*fontsize, y+0.35*fontsize
  elif length == 4: #four digits
    return x+fontsize, y+0.35*fontsize
  #how many songs do you intend to have??
  return x+2*fontsize, y+0.35*fontsize

def cover_page(canvas, doc):
  """Defines the cover page layout."""

  from reportlab.lib.units import cm

  canvas.saveState()

  # draws the rectangle with the site name in vertical form
  # remember: coordinates (0,0) start at bottom left and go up and to the
  # right!
  canvas.setFillGray(0)
  page_height = doc.bottomMargin + doc.height + doc.topMargin
  page_width = doc.leftMargin + doc.width + doc.rightMargin
  x = page_width - doc.leftMargin
  rect_width = page_width - x 
  canvas.rect(x, 0, rect_width, page_height, fill=True, stroke=False) 

  canvas.rotate(90)
  t = canvas.beginText()
  font_size = 20 
  t.setTextOrigin(doc.bottomMargin, -x-font_size-2)
  t.setFont('Times-Bold', font_size)
  t.setFillGray(0.75)
  t.textLine(u"http://%s" % (Site.objects.get_current().domain))
  canvas.drawText(t)

  canvas.restoreState()

def toc_page(canvas, doc):
  from reportlab.lib.colors import Color
  from reportlab.lib.units import cm
  
  canvas.saveState()

  # draws the rectangle with the performer name and picture
  # remember: coordinates (0,0) start at bottom left and go up and to the
  # right!
  canvas.setFillGray(0.0)
  page_height = doc.bottomMargin + doc.height + doc.topMargin
  page_width = doc.leftMargin + doc.width + doc.rightMargin
  y = page_height - doc.topMargin + 0.2*cm # a bit above the top margin
  rect_height = page_height - y
  canvas.rect(0, y, page_width, rect_height, fill=True, stroke=False) 

  name = canvas.beginText()
  name.setTextOrigin(doc.leftMargin, y+0.4*cm)
  name.setFont('Helvetica-Bold', 20)
  name.setFillGray(1)
  name.textLine(ugettext(u'Table of Contents'))
  canvas.drawText(name)

  def int_to_roman(input):
    """ Convert an integer to a Roman numeral. """
    if not isinstance(input, type(1)):
      raise TypeError, "expected integer, got %s" % type(input)
    if not 0 < input < 4000:
      raise ValueError, "Argument must be between 1 and 3999"
    ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
    nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
    result = []
    for i in range(len(ints)):
      count = int(input / ints[i])
      result.append(nums[i] * count)
      input -= ints[i] * count
    return ''.join(result)

  def page_circle_center(x, y, fontsize, value):
    """Calculates the approximate circle center given the page positioning,
    fontsize and its current value."""
    length = len(str(value)) #the field length

    if length == 1: #only one digit in the page
      return x+0.15*fontsize, y+0.35*fontsize
    elif length == 2: #two digits in the page
      return x+0.30*fontsize, y+0.35*fontsize
    return x+0.45*fontsize, y+0.35*fontsize

  # Draws song name and page number
  page_x = doc.width+doc.rightMargin+0.5*cm
  page_y = doc.bottomMargin-cm
  page_fontsize = 11 
  page = canvas.beginText()
  page.setTextOrigin(page_x, page_y)
  page.setFont('Helvetica-Bold', page_fontsize)
  page.setFillGray(1)
  page_number = int_to_roman(doc.page).lower()
  page.textLine(page_number)

  #circle around number
  canvas.setFillGray(0.0)
  circle_x, circle_y = page_circle_center(page_x, page_y,
      page_fontsize, page_number)
  canvas.circle(circle_x, circle_y, 1.5*page_fontsize, fill=True,
      stroke=False)
  
  canvas.drawText(page)

  canvas.restoreState()

def set_basic_templates(doc):
  from reportlab.platypus.frames import Frame
  from reportlab.platypus.doctemplate import PageTemplate
  from reportlab.lib.units import cm

  doc._calc() #taken from reportlab source code (magic)

  templates = []

  #the front page framing
  cover_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
      leftPadding=0, rightPadding=10, topPadding=3*cm, bottomPadding=5*cm)
  templates.append(PageTemplate(id='Cover', frames=cover_frame,
    onPage=cover_page, pagesize=doc.pagesize))

  #normal frame, for the TOC
  frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
      id='normal', rightPadding=0, leftPadding=0)
  templates.append(PageTemplate(id='TOC', frames=frame, onPage=toc_page,
    pagesize=doc.pagesize))
  
  doc.addPageTemplates(templates)


class SongBookTemplate(BaseDocTemplate):

  def __init__(self, *args, **kwargs):
    BaseDocTemplate.__init__(self, *args, **kwargs)
    set_basic_templates(self)

  def afterFlowable(self, flowable): 
    """Registers TOC entries in our Doc Templates."""

    if flowable.__class__.__name__ == 'Paragraph' and \
        flowable.style.name == 'song-title':
      key = 'song-title-%s' % self.seq.nextf('song-title')
      self.canv.bookmarkPage(key)
      self.notify('TOCEntry', (0, flowable.getPlainText(), self.page, key)) 


def pdf_cover_page(songs, request):
  """Bootstraps our PDF sequence of flowables."""
  from pdf import style
  from reportlab.platypus import Paragraph, Spacer, PageBreak
  from reportlab.lib.units import cm
  from time import strftime

  story = []
  story.append(Paragraph(ugettext(u'<i>Chordbook</i><br/><b>%(site)s</b>') % \
      {'site': Site.objects.get_current().name}, style['cover-title']))
  story.append(Spacer(1, 3*cm))

  if songs.count():
    update_date = songs.order_by('-updated')[0].updated.strftime('%a, %d/%b/%Y')
  else:
    update_date = u''
  story.append(Paragraph(ugettext(u'Last update: <b>%(update)s</b><br/>%(url)s<br/>Downloaded on %(date)s') % \
      {
       'update': update_date,
       'url': request.build_absolute_uri(),
       'date': strftime('%a, %d/%b/%Y'),
      },
      style['cover-subtitle']))
  return story

