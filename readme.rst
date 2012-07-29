This repository contains some fairly crude but functional tools for converting
laTeX and Bibtex files to ReStructured Text (.rst) and html files. The tex2rst functions
are in many places specific to converting old Clawpack documentation, but may
still be a useful starting place for other purposes. Also, note that these do
not constitute a real TeX parser by any stretch of the imagination. The
bibtex2rst module mainly uses the bibliograph.parser module. Other tools exist,
but seem to be fragile or have very poor documentation.

Requires bibliograph.parsing, bibliograph.rendering, zope.component, and zope.schema::

    $ pip install bibliograph.parsing
    $ pip install bibliograph.rendering
    $ pip install zope.component
    $ pip install zope.schema
