#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Created by Andre Anjos <andre.dos.anjos@cern.ch>
# Sat 27 Mar 08:42:10 2010 

"""Tags for chords.
"""

from django import template
register = template.Library()
 
@register.inclusion_tag('chords/paginator.html')
def chords_paginator(paginator):
  return {'paginator': paginator}

@register.inclusion_tag('chords/sorter.html')
def chords_sorter(what):
  return {'what': what}

