#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 04 Oct 2010 16:36:48 CEST 

"""A simple parser for Chord Pro files.
"""

import re, codecs

class Verse:
  """A verse."""

  def __init__(self):
    self.lines = []
    self.ended = False

  def append(self, line):
    """Adds another line into this verse. This includes parsing."""
    if not self.ended: self.lines.append(line)
    else:
      raise SyntaxError, 'Cannot append to Verse started at line %d, it has been closed on line %d' % (self.lines[0].lineno, self.lines[-1].lineno) 

  def end(self, line=0): #we don't accumulate the last line
    """Ends this verse."""
    self.ended = True

  def __str__(self):
    v = ['--- Verse:']
    v += [str(k) for k in self.lines]
    v.append('--- End verse')
    return '\n'.join(v)

class Chorus(Verse):
  """A complete chorus entry."""

  def __init__(self, start):
    Verse.__init__(self)
    self.starts = start
    self.ends = None
    self.lines = []

  def append(self, line):
    if not self.ended: self.lines.append(line)
    else:
      raise SyntaxError, 'Cannot append to Chorus started at line %d, it has been closed on line %d' % (self.starts.lineno, self.ends.lineno)

  def end(self, end):
    self.ends = end

  def __str__(self):
    v = [self.starts]
    v += [str(k) for k in self.lines]
    v.append(self.ends)
    return '\n'.join([str(k) for k in v])

class Tablature(Verse):
  """A complete tablature entry."""

  def __init__(self, start):
    Verse.__init__(self)
    self.starts = start
    self.ends = None
    self.lines = []

  def append(self, line):
    if not self.ended: self.lines.append(line)
    else:
      raise SyntaxError, 'Cannot append to Tablature started at line %d, it has been closed on line %d' % (self.starts.lineno, self.ends.lineno)

  def end(self, end):
    self.ends = end

  def __str__(self):
    v = [self.starts]
    v += [str(k) for k in self.lines]
    v.append(self.ends)
    return '\n'.join([str(k) for k in v])

class EmptyLine:
  """A line with nothing."""

  def __init__(self, lineno):
    self.lineno = lineno

  def __str__(self):
    return '%03d ' % (self.lineno,)

class HashComment(EmptyLine):
  """A hash comment is a line that starts with a # mark."""

  def __init__(self, v, lineno):
    EmptyLine.__init__(self, lineno)
    self.comment = v

  def __str__(self):
    return '%03d %s' % (self.lineno, self.comment)

class Command:
  """A generic command from chordpro."""

  def __init__(self, lineno):
    self.lineno = lineno

class StartOfChorus(Command):
  """A start of chorus marker."""

  def __init__(self, lineno):
    Command.__init__(self, lineno)
  
  def __str__(self):
    return '%03d {start_of_chorus}' % (self.lineno)

class EndOfChorus(Command):
  """A end of chorus marker."""

  def __init__(self, lineno):
    Command.__init__(self, lineno)

  def __str__(self):
    return '%03d {end_of_chorus}' % (self.lineno)

class StartOfTablature(Command):
  """A start of tablature marker."""

  def __init__(self, lineno):
    Command.__init__(self, lineno)

  def __str__(self):
    return '%03d {start_of_tab}' % (self.lineno)

class EndOfTablature(Command):
  """A end of tablature marker."""

  def __init__(self, lineno):
    Command.__init__(self, lineno)

  def __str__(self):
    return '%03d {end_of_tab}' % (self.lineno)

class Comment(Command):
  """A chordpro {comment:...} entry."""

  def __init__(self, lineno, value):
    Command.__init__(self, lineno)
    self.value = value
  
  def __str__(self):
    return '%03d {comment: %s}' % (self.lineno, self.value)

class UnsupportedCommand(Command):
  """One of the chordpro commands we don't support."""

  def __init__(self, command, value, lineno):
    Command.__init__(self, lineno)
    self.command = command
    self.value = value

  def __str__(self):
    return '%03d {%s: %s} [UNSUPPORTED]' % \
        (self.lineno, self.command, self.value)

class CommandParser:
  """Parses and generates the proper command from the input."""

  comment = re.compile(r'{\s*(comment|c)\s*:\s*(?P<v>.*)}', re.I)
  soc = re.compile(r'{\s*(start_of_chorus|soc)\s*}', re.I)
  eoc = re.compile(r'{\s*(end_of_chorus|eoc)\s*}', re.I)
  sot = re.compile(r'{\s*(start_of_tab|sot)\s*}', re.I)
  eot = re.compile(r'{\s*(end_of_tab|eot)\s*}', re.I)
  define = re.compile(r'{\s*(define)\s+(?P<v>.*)}', re.I)
  title = re.compile(r'{\s*(title|t)\s*:\s*(?P<v>.*)}', re.I)
  subtitle = re.compile(r'{\s*(subtitle|st)\s*:\s*(?P<v>.*)}', re.I)

  def __init__(self):
    pass

  def __call__(self, v, lineno):
    if CommandParser.comment.match(v): return Comment(lineno, CommandParser.comment.match(v).group('v'))
    elif CommandParser.soc.match(v): return StartOfChorus(lineno)
    elif CommandParser.eoc.match(v): return EndOfChorus(lineno)
    elif CommandParser.sot.match(v): return StartOfTablature(lineno)
    elif CommandParser.eot.match(v): return EndOfTablature(lineno)
    elif CommandParser.define.match(v): 
      return UnsupportedCommand('define', CommandParser.define.match(v).group('v'), lineno)
    elif CommandParser.title.match(v): 
      return UnsupportedCommand('title', CommandParser.title.match(v).group('v'), lineno)
    elif CommandParser.subtitle.match(v): 
      return UnsupportedCommand('subtitle', CommandParser.subtitle.match(v).group('v'), lineno)
    
    #we don't do anything if the command is unsupported
    return HashComment('#' + v + ' [IGNORED]', lineno)

class Line:
  """A line that contains information of some sort."""

  def __init__(self, v, lineno):
    self.lineno = lineno
    self.value = v.decode

  def __str__(self):
    return '%03d %s' % (self.lineno, self.value)

class ChordLine(Line):
  """A special category of line that contains chords."""

  def __init__(self, v, lineno):
    Line.__init__(self, v, lineno)
    self.bare = LineParser.chord.sub('', self.value, re.UNICODE)
    self.chords = []
    subtract = 0 
    for z in LineParser.chord.finditer(self.value):
      self.chords.append((z.start()-subtract, z.groups()[0]))
      subtract = z.end() + (z.end() - z.start()) - 2

  def __str__(self):
    cline = '    '
    for c in self.chords: cline += (' '*c[0] + c[1].capitalize())
    v = [cline, '%03d %s' % (self.lineno, self.bare)]
    return '\n'.join(v)

class LineParser:

  chord = re.compile(r'\[(?P<v>[^\]]*)\]')

  def __init__(self):
    pass

  def __call__(self, l, lineno):
    if LineParser.chord.search(l): return ChordLine(l, lineno)
    return Line(l, lineno)

def parse(f):
  """Parses a chord-pro formatted file and turns the input into low-level
  constructs that can be easily analyzed by our high-level syntax parser."""  

  d = codecs.open(f, 'rt', 'utf-8')
  input = []
  cmdparser = CommandParser()
  lineparser = LineParser()
  for i, l in enumerate(d):
    sl = l.strip()
    if not sl: input.append(EmptyLine(i+1))
    elif sl[0] == '#': input.append(HashComment(sl, i+1))
    elif sl[0] == '{': input.append(cmdparser(sl, i+1))
    else: input.append(lineparser(l.rstrip(), i+1))
  d.close()

  return input

def consume_chorus(input):
  """This method will consume the whole of a chorus section until an end marker
  is found."""
  if not input: return []
 
  if isinstance(input[0], StartOfChorus):
    retval = Chorus(input.pop(0))
  else: 
    return []

  while True:
    try:
      i = input.pop(0)
      if isinstance(i, EndOfChorus):
        retval.end(i)
        return [retval]
      elif isinstance(i, Comment):
        retval.append(i)
      elif isinstance(i, (Command,)):
        raise SyntaxError, 'Line %d: Cannot have command inside Chorus.' % \
            i.lineno
      else:
        retval.append(i)
    except IndexError: #input has ended w/o closing
      return [retval]

def consume_tablature(input):
  """This method will consume the whole of a tablature section until an end 
  marker is found."""
  if not input: return []
  
  if isinstance(input[0], StartOfTablature):
    retval = Chorus(input.pop(0))
  else: 
    return []

  while True:
    try:
      i = input.pop(0)
      if isinstance(i, EndOfTablature):
        retval.end(i)
        return [retval]
      elif isinstance(i, Comment):
        retval.append(i)
      elif isinstance(i, (Command,)):
        raise SyntaxError, 'Line %d: Cannot have command inside Tablature.' % \
            i.lineno
      else:
        retval.append(i)
    except IndexError: #input has ended w/o closing
      return retval

def consume_extra(input):
  """Consumes all empty lines and comments that follow."""
  retval = []

  try:
    while isinstance(input[0], (EmptyLine, HashComment, Comment, UnsupportedCommand)):
      retval.append(input.pop(0))
  except IndexError: #input has ended
    pass

  return retval

def consume_verse(input):
  """Consumes the whole of a verse."""
  if not input: return []
  if isinstance(input[0], Line):
    retval = Verse()
    retval.append(input.pop(0))
  else:
    return []

  try:
    while not isinstance(input[0], (EmptyLine, HashComment, Command)):
      retval.append(input.pop(0))
  except IndexError: #input has ended
    pass

  retval.end()
  return [retval]

def syntax_analysis(input):
  """Syntax analysis groups low-level constructs to make up Choruses,
  Tablatures and Verses."""

  retval = []

  # Makes sure we don't have any syntactical problems
  while input:
    save_length = len(input)
    retval += consume_extra(input)
    retval += consume_verse(input)
    retval += consume_chorus(input)
    retval += consume_tablature(input)
    if save_length == len(input): #nothing was consumed
      raise SyntaxError, 'Cannot make sense of "%s"' % (input[0])

  return retval 

if __name__ == '__main__':
  import os, sys

  if len(sys.argv) == 1:
    print 'usage: %s <file.chord>' % os.path.basename(sys.argv[0])
    sys.exit(1)

  items = syntax_analysis(parse(sys.argv[1]))
  print 'File %s contains %d blocks' % (sys.argv[1], len(items))
  for k in items: print k
