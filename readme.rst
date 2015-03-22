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

You should clone or download this repository and put it on your PYTHONPATH.
There are various tools included, but the one I mainly use and continue
to develop is the bibtex to html bit.  It can be used as follows:

    cd /directory/with/my/bibtex/file/
    ipython
    from tex2rst import bibtex2htmldiv
    bibtex2htmldiv.bib2html('mybibtexfile.bib')

Then copy the contents of `bib.html` into your HTML page, preferably
with appropriate CSS defined.  For example, the CSS I use on my own site
is as follows:

    #pub {padding: 5px; 
          border-width: 2px; 
          border-style: none; 
          background-color: #fff; 
          font-size: 1.1em;
          line-height: 1.1em;
          margin-top: 5px;
          margin-right: 1%;
          margin-bottom: 5px;
          vertical-align: middle;}

    #pub a{font-weight: bold; color: #09434e;}
    #pub name{font-weight: bold; color: #09434e;}
    #pub journal{font-style: italic;}
    #pub links{ font-weight: bold; color: black; vertical-align: bottom;}
    #pub links a{ font-weight: bold; color: maroon; font-style: italic;}
    #pub img{height: 4em; align: right; padding-right: 3px;}

If you want to include links to your papers beyond what is in the bibtex file,
modify `paperlinks.py`.
