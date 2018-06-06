"""
Convert bibtex files (.bib) to Sphinx-formatted bibliography files.
Usage:
    >> from bibtex2rst import bibtex2rst
    >> bibtex2rst.bib2rst('/path/to/myfile.bib')

"""

def bib2rst(bibfile,rstfile='bib.rst'):
    entries=parsefile(bibfile)
    writebib(entries,rstfile)

def parsefile(filename):
    """
    Takes a file name (string, including path) and returns a list of dictionaries,
    one dictionary for each bibtex entry in the file.

    Uses the bibliograph.parsing package.
    """
    from bibliograph.parsing.parsers.bibtex import BibtexParser
    bp=BibtexParser()

    f=file(filename)
    ents = [bp.parseEntry(x) for x in bp.splitSource(f.read())]
    f.close()

    #Parsing errors give strings, so keep only dicts:
    entries=[x for x in ents if x.__class__ is dict]
    return entries

def writebib(entries,filename='bib.rst'):
    """
    Writes ReStructured Text citation entries.
    This only works well for articles so far; for other citation types,
    it merely writes the author, title, and year.  It should be easy to
    add better functionality for other types.
    """
    f=file(filename,'w')

    f.write('================\n')
    f.write('Bibliography\n')
    f.write('================\n')

    for entry in entries:
        f.write(".. [%s] " % entry['pid'])
        f.write("%s, " % entry['author'][0])
        f.write("*%s*" % entry['title'])
        if 'journal' in entry.keys():
            f.write(", %s" % entry['journal'])
            if 'volume' in entry.keys():
                f.write(", %s" % entry['volume'])
                if 'number' in entry.keys():
                    f.write("(%s)" % entry['number'])
                    if 'pages' in entry.keys():
                        f.write(":%s" % entry['pages'].replace('&ndash;','-'))
        try:
            f.write(" (%s)" % entry['year'])
        except KeyError:
            print('No year in entry %s' % entry['pid'])
        f.write("\n\n")

    f.close()
