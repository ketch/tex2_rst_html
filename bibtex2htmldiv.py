"""
Convert bibtex files (.bib) to html divs that can be custom formatted using CSS.
Usage (from Python or IPython prompt):

    >> import bibtex2htmldiv
    >> bibtex2htmldiv.bib2html('/path/to/myfile.bib')

"""
import os
import pybtex.database
import json
import ast

# This may need to be changed for other machines/users
img_path = r'/Users/ketch/Box Sync/My Papers/paper_images/'
# This may need to be changed for other sites
img_dest = 'http://davidketcheson.info/assets/paper_images/'
paperlinks_path = '/Users/ketch/Research/Projects/labnotebook/assets/paperlinks.txt'

def bib2html(bibfile,htmlfile='bib.html'):
    publications=parsefile(bibfile)
    writebib(publications,htmlfile)

def compile_name(person):
    first = ' '.join([x.render_as('text') for x in person.rich_first_names])
    middle = ' '.join([x.render_as('text') for x in person.rich_middle_names])
    last = ' '.join([x.render_as('text') for x in person.rich_last_names])
    return first+' '+middle+' '+last

def parsefile(filename):
    """
    Takes a file name (string, including path) and returns a list of dictionaries,
    one dictionary for each bibtex entry in the file.

    Uses the bibliograph.parsing package.
    """
    with open(filename) as f:
        db = pybtex.database.parse_string(f.read(),'bibtex')
    blist = [db.entries[key] for key in db.entries.keys()]
    publications = []
    for entry in blist:
        publications.append({x:entry.fields[x] for x in entry.fields.keys()})
        publications[-1]['pid'] = entry.key
        publications[-1]['reference_type'] = entry.type
        publications[-1]['author'] = [compile_name(p) for p in entry.persons['Author']]

    # Parsing errors give strings, so keep only dicts:
    #publications=[x for x in ents if x.__class__ is dict]
    return publications

def normalize_authors(authors):
    """
    Takes the authors string from a bibtex entry and rewrites it with
    first names first.
    """
    authorlist = authors
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
    f=open(filename,'w')

    write_section('Submitted preprints','unpublished',publications,f)
    write_section('Refereed Journal Articles','article',publications,f)
    write_section('Books','book',publications,f)
    write_section('Conference Proceedings','inproceedings',publications,f)
    write_section('Technical Reports','techreport',publications,f)
    write_section('Theses','phdthesis',publications,f)

    f.close()


def write_section(title,reference_type,publications,f):
    """
    Write out all entries of type reference_type, in reverse chronological order
    """
    these_pubs = [pub for pub in publications if pub['reference_type']==reference_type]
    these_pubs=sort_by_year(these_pubs)
    print(len(these_pubs))
    if len(these_pubs)>0:
        f.write('<h2>'+title+'</h2>\n')
        for pub in these_pubs: write_entry(pub,f)


def write_entry(pub,f):
    pub['author'] = normalize_authors(pub['author'])

    f.write('<div id="pub" class="pub filterable ')
    if 'Keywords' in pub:
        f.write(pub['Keywords'].lower().replace(';',' ').replace(',',' '))
    f.write('">\n')
    img_file = img_path + pub['pid'] + '.png'
    print(img_file)
    if os.path.isfile(os.path.abspath(img_file)):
        f.write('<img src="' + img_dest + pub['pid'] + '.png" align="right" />\n')
    if 'Url' in pub:
        f.write('<a href="'+pub['Url'].split()[0].replace('\_','_')+'">')
    elif 'Doi' in pub.keys():
        f.write('<a href="https://doi.org/'+pub['Doi']+'">')
    elif 'Arxivid' in pub:
        f.write('<a href="http://arxiv.org/abs/'+pub['Arxivid']+'">')
    f.write('<name> %s </name><br>\n' % pub['Title'].replace('{','').replace('}',''))
    if ('Url' in pub) or ('Doi' in pub) or ('Arxivid' in pub):
        f.write('</a>\n')
    f.write('<authors> %s</authors>,\n' % pub['author'])
    if 'Journal' in pub.keys():
        f.write('<journal> %s</journal>' % pub['Journal'])
        if 'Volume' in pub.keys():
            f.write(", %s" % pub['Volume'])
            if 'Number' in pub.keys():
                f.write("(%s)" % pub['Number'])
                if 'Pages' in pub.keys():
                    f.write(":%s" % pub['Pages'].replace('&ndash;','-'))
    if 'Annote' in pub.keys():
        f.write(" %s" % pub['Annote'])
    if 'School' in pub.keys():
        f.write(" %s," % pub['School'])
    if 'Booktitle' in pub.keys():
        f.write("in %s." % pub['Booktitle'])
    if pub['Year'] != '':
        f.write(" (%s)" % pub['Year'])

    # Write links line
    linkstring = ''

    if 'Url' in pub.keys():
        if 'arxiv' not in pub['Url'].split()[0]:
            if 'davidketcheson' in pub['Url'].split()[0]:
                linkstring += ' | <a href="'+pub['Url'].split()[0]+'">Free PDF</a> '
    if 'Doi' in pub.keys():
        linkstring += ' | <a href="https://doi.org/'+pub['Doi']+'">Published version</a> '
    if 'Arxivid' in pub.keys():
        linkstring += ' | <a href="http://arxiv.org/abs/'+pub['Arxivid']+'">arXiv version</a> '

    with open(paperlinks_path, 'r') as f2:
        links = ast.literal_eval(f2.read())
    if pub['pid'] in links.keys():
        publinks = links[pub['pid']]
        for name, link in publinks.items():
            linkstring += ' | <a href="'+link+'">'+name+'</a> '

    if len(linkstring)>0:
        f.write('<br>\n<links> ')
        f.write(linkstring)
        f.write('|</links>')
    f.write('<div style="clear:both"></div>\n')
    f.write('\n</div>\n\n')

def sort_by_year(publications):
    """Takes a list of publications and return it sorted in reverse chronological order."""
    return sorted(publications, key=lambda p: p.setdefault('Year',''),reverse=True)
