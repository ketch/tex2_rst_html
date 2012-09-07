"""
Convert bibtex files (.bib) to html divs that can be custom formatted using CSS.
Usage:
    >> import bibtex2htmldiv
    >> bibtex2htmldiv.bib2html('/path/to/myfile.bib')

"""

def bib2html(bibfile,htmlfile='bib.html'):
    publications=parsefile(bibfile)
    writebib(publications,htmlfile)

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
    publications=[x for x in ents if x.__class__ is dict]
    return publications

def normalize_authors(authors):
    """
    Takes the authors string from a bibtex entry and rewrites it with
    first names first.
    """
    authorlist = authors.split('and ')
    authornames=[]
    for author in authorlist:
        if ',' in author:
            lastname, firstname = author.split(',')
            authornames.append(firstname.strip()+' '+lastname.strip())
        else:
            authornames.append(author.strip())
    if len(authorlist)>1:
        authornames[-1] = ' and '+authornames[-1]
    if len(authorlist)>2:
        return ', '.join(authornames)
    else:
        return ' '.join(authornames)

def writebib(publications,filename='bib.rst'):
    """
    Writes html citation entries.
    This only works well for articles so far; for other citation types,
    it merely writes the author, title, and year.  It should be easy to
    add better functionality for other types.

    To Do:
        - Sections for different publication types or years
        - links
        - bibtex?
        - doi
    """
    f=file(filename,'w')

    write_section('Preprints','UnpublishedReference',publications,f)
    write_section('Refereed Journal Articles','ArticleReference',publications,f)
    write_section('Books','BookReference',publications,f)
    write_section('Conference Proceedings','InproceedingsReference',publications,f)
    write_section('Technical Reports','TechreportReference',publications,f)
    write_section('Theses','PhdthesisReference',publications,f)

    f.close()

def write_section(title,reference_type,publications,f):
    """
    Write out all entries of type reference_type, in reverse chronological order
    """
    these_pubs = [pub for pub in publications if pub['reference_type']==reference_type]
    these_pubs=sort_by_year(these_pubs)
    if len(these_pubs)>0:
        f.write('<h2>'+title+'</h2>\n')
        for pub in these_pubs: write_entry(pub,f)

def write_entry(pub,f):
    pub['author'][0] = normalize_authors(pub['author'][0])

    f.write('<div id="pub">\n')
    if pub.has_key('url'):
        f.write('<a href="'+pub['url'].split()[0].replace('\_','_')+'">')
    f.write('<name> %s </name><br>\n' % pub['title'])
    if pub.has_key('url'):
        f.write('</a>\n')
    f.write('<authors> %s</authors>,\n' % pub['author'][0])
    if 'journal' in pub.keys():
        f.write('<journal> %s</journal>' % pub['journal'])
        if 'volume' in pub.keys():
            f.write(", %s" % pub['volume'])
            if 'number' in pub.keys():
                f.write("(%s)" % pub['number'])
                if 'pages' in pub.keys():
                    f.write(":%s" % pub['pages'].replace('&ndash;','-'))
    if 'annote' in pub.keys():
        f.write(" %s" % pub['annote'])
    if pub['year'] != '':
        f.write(" (%s)" % pub['year'])

    # Write links line
    f.write('<br>\n<links> ')
    if 'url' in pub.keys():
        f.write(' | <a href="'+pub['url'].split()[0]+'">Download</a> | ')
    if 'doi' in pub.keys():
        f.write(' | <a href="http://dx.doi.org/'+pub['doi']+'">DOI</a> | ')
    if 'ARXIVID' in pub.keys():
        f.write(' | <a href="http://arxiv.org/abs/'+pub['ARXIVID']+'">arXiv</a> | ')
    f.write('</links>')

    f.write('\n</div>\n\n')

def sort_by_year(publications):
    """Takes a list of publications and return it sorted in reverse chronological order."""
    return sorted(publications, key=lambda p: p.setdefault('year',''),reverse=True)
