Chordpro Format
===============

Django-chords stores songs in the chordpro format, a simple format for notation 
of lyrics together with chords. Use your popular Internet search engine to find
huge collections of songs in chordpro format in the Word Wide Web.

In the chordpro format chords are denoted in square brackets [] in the text,
e.g.

[Em]Alas, my [G]love, you [D]do me [Bm]wrong,

Should be rendered as something like this:

Em       G         D     Bm
Alas, my love, you do me wrong,

Jumping one or more lines, defines a verse.

In addition to the chords in square brackets, the chordpro format defines
several control sequences in curly brackets {}. Django-chords understands the
following control statements:

{comment: ...} or {c: ...} Comment, e.g. Repeat 2x or Chorus. Comments are rendered inverse.

{soc}, {start_of_chorus} and {eoc}, {end_of_chorus} Start and end of chorus. Chorus is indicated by a black line to the left.

{sot}, {start_of_tab} and {eot}, {end_of_tab} Start and end of tab. A tab (tablature) section is rendered in a fixed width font.

# Lines starting with # are comment lines and are ignored in the song view.

Please note the control sequences cannot be combined on the same line with the
lyrics.

The following statements are ignored by Django-chords as we have special
database fields for those.

{define ...} Used to define a special chord for this song. The chord format is
<chord name> <base fret> <string 6> ...<string 1>, i.e.  G 1 3 2 0 0 0 3

{title: ...} or {t: ...} Song title. This is displayed in the song list screen and in the title bar.

{subtitle: ...} or {st: ...} Song subtitle, typically the interpret or composer. This is displayed in the song list screen and in the title bar.
