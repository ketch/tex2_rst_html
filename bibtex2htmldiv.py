"""
Convert bibtex files (.bib) to html divs that can be custom formatted using CSS.
Usage:
    >> import bibtex2htmldiv
    >> bibtex2htmldiv.bib2html('/path/to/myfile.bib')

"""
import os
# This may need to be changed for other machines/users
img_path = r'/Users/ketch/Box Sync/My Papers/paper_images/'
# This may need to be changed for other sites
img_dest = 'http://davidketcheson.info/assets/paper_images/'

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
    """
    f=file(filename,'w')

    write_section('Submitted preprints','UnpublishedReference',publications,f)
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

    f.write('<div id="pub" class="pub filterable ')
    if pub.has_key('keywords'):
        f.write(' '.join(pub['keywords']).lower().replace(';',''))
    f.write('">\n')
    img_file = img_path + pub['pid'] + '.png'
    print img_file
    if os.path.isfile(os.path.abspath(img_file)):
        f.write('<img src="' + img_dest + pub['pid'] + '.png" align="right" />\n')
    if pub.has_key('url'):
        f.write('<a href="'+pub['url'].split()[0].replace('\_','_')+'">')
    elif 'doi' in pub.keys():
        f.write('<a href="http://dx.doi.org/'+pub['doi']+'">')
    elif pub.has_key('ARXIVID'):
        f.write('<a href="http://arxiv.org/abs/'+pub['ARXIVID']+'">')
    f.write('<name> %s </name><br>\n' % pub['title'])
    if pub.has_key('url') or pub.has_key('doi') or pub.has_key('ARXIVID'):
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
    if 'school' in pub.keys():
        f.write(" %s," % pub['school'])
    if 'booktitle' in pub.keys():
        f.write("in %s." % pub['booktitle'])
    if pub['year'] != '':
        f.write(" (%s)" % pub['year'])

    # Write links line
    linkstring = ''

    if 'url' in pub.keys():
        if 'arxiv' not in pub['url'].split()[0]:
            if 'davidketcheson' in pub['url'].split()[0]:
                linkstring += ' | <a href="'+pub['url'].split()[0]+'">Free PDF</a> '
    if 'doi' in pub.keys():
        linkstring += ' | <a href="http://dx.doi.org/'+pub['doi']+'">Published version</a> '
    if 'ARXIVID' in pub.keys():
        linkstring += ' | <a href="http://arxiv.org/abs/'+pub['ARXIVID']+'">arXiv version</a> '

    try:
        from paperlinks import links
        if pub['pid'] in links.keys():
            publinks = links[pub['pid']]
            for name, link in publinks.iteritems():
                linkstring += ' | <a href="'+link+'">'+name+'</a> '
    except:
        print 'paperlinks.py not found; continuing...'

    if len(linkstring)>0:
        f.write('<br>\n<links> ')
        f.write(linkstring)
        f.write('|</links>')
    f.write('<div style="clear:both"></div>\n')
    f.write('\n</div>\n\n')

def sort_by_year(publications):
    """Takes a list of publications and return it sorted in reverse chronological order."""
    return sorted(publications, key=lambda p: p.setdefault('year',''),reverse=True)
