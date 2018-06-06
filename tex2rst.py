
#======================
def clawdocconvert():
#======================
    tex2rst('chapter1','basic')
    tex2rst('chapter2','matlab')
    tex2rst('chapter3','amrclaw')
    tex2rst('chapter4','mpiclaw')

#==========================================
def tex2rst(infile='chapter1',outfile=''):
#==========================================
    """
        Convert a LaTeX file to reStructured Text.
        Does the following:
            #. Look for headers (chapter, section, etc.) and
               convert them to reST headers (including converting
               LaTeX labels to reST references).
            #. Text formatting (italics, boldface, monotype, etc.)
            #. Convert TeX lists to reST lists
    """
    headers=[('\chapter{','*',1),
             ('\section{','=',0),
             ('\subsection{','-',0),
             ('\subsection*{','-',0)]

    styles=[('{\\em','*',0,5),
            ('\\verb+','``',5,1),
            ('{\\bf','**',0,5),
            ('{\\large\\bf','**',0,11),
            ('{\\sc','**',0,5),
            ('\\texttt{','``',7,1),
            ('\\textsc{','**',7,1),
            ('\\textbf{','**',7,1),
            ('{\\tt','``',0,5)]

    open_list_count = 0
    enum = 0
    verbatim=0
    in_eqn=0
    ignore=0


    if outfile=='': outfile=infile
    input=open(infile+'.tex','rU')
    output=open(outfile+'.rst','w')

    i=-1
    lines=input.readlines()
    while i<len(lines)-1:
        i=i+1
        outline=lines[i]
        if outline.count('%'): 
            pos=outline.find('%')
            outline=outline[:pos]

        outline=outline.replace("``","*")
        outline=outline.replace("''","*")

        # Detect ignore blocks
        if outline.count('\\ignore{') or ignore>0:
            ignore+=outline.count('{')
            ignore-=outline.count('}')
            continue

        # Detect lists
        if outline.count('\\begin{description}') or outline.count('\\bi\n') or outline.count('\\begin{itemize}') or outline=='\\be\n':
            if outline=='\\be\n': enum=1
            open_list_count += 1
            output.write('\n')
            continue
        if outline.count('\\end{description}') or outline.count('\\ei') or outline.count('\\end{itemize}') or outline=='\\ee\n':
            if outline=='\\ee\n': enum=0
            open_list_count -= 1
            output.write('\n')
            continue
        if outline.count('\\begin{verbatim}'):
            verbatim=1
            if open_list_count:
                if enum:
                    output.write('\n'+' '*(4*open_list_count)+'   '+'::\n\n')
                else:
                    output.write('\n'+' '*(4*open_list_count)+'  '+'::\n\n')
            else:
                output.write('\n::\n\n')
            continue
        if outline.count('\\end{verbatim}'):
            verbatim=0
            output.write('\n')
            continue

        #Detect equations
        if outline.count('\\enmno'):
            outline=outline.replace('\\enmno','\\\\end{eqnarray*}')
            in_eqn = 0

        if outline.count('\\end{equation}'):
            outline=outline.replace('\\end{equation}','\\\\end{equation}')
            in_eqn = 0

        if in_eqn:
            outline=outline.replace('\\','\\\\')
            outline=outline.replace('|','\|')
            outline=outline.replace('&','\&')
            outline=outline.replace('\\\\\n','\\\\ \n')
        else:
            outline=outline.replace('\\\n','\n')

        if outline.count('\\eql{'):
            in_eqn = 1
            # First grab label 
            pos=outline.find('\\eql{')+4
            label=get_substring(outline,pos)
            outline=outline.replace('\\eql'+label,'\\\\begin{equation}')

        if outline.count('\\begin{equation}'):
            in_eqn = 1
            outline=outline.replace('\\begin{equation}'+label,'\\\\begin{equation}')
                
        if outline.count('\\eqmno'):
            in_eqn = 1
            outline=outline.replace('\\eqmno','\\\\begin{eqnarray*}')
                
#            outline='.. _'+label.replace(':','-')[1:-1]+':\n\n'+outline
 
        #Process this line:
        # Format special strings specific to ClawPack
        outline=outline.replace("\\claw\\","**ClawPack**")
        outline=outline.replace("\\amrclaw\\","**AMRClaw**")
        outline=outline.replace("\\matlab\\","**MATLAB**")

        outline=outline.replace('\\\n','\n\n')

        # Process headers
        for header,symbol,overline in headers:
            if outline.count(header):
                # First grab label (if any)
                if outline.count('\\label{'):
                    pos=outline.find('\\label{')+6
                    label=get_substring(outline,pos)
                    outline=outline.replace('\\label'+label,'')
                    outline='.. _'+label.replace(':','-')[1:-1]+':\n\n'+outline
                # Now grab the title
                pos=outline.find(header)+len(header)-1
                title=get_substring(outline,pos)
                if overline:
                    outline=outline.replace(header+title[1:],symbol*len(title)+
                        '\n'+title[1:-1]+'\n'+symbol*len(title)+'\n')
                else:
                    outline=outline.replace(header+title[1:],title[1:-1]+'\n'+
                        symbol*len(title)+'\n')
    
        for style,markup,offset,offset2 in styles:
            while outline.count(style):

                # First make sure that braced blocks are fully grabbed
                while outline.count('{')>outline.count('}'):
                    i=i+1
#                    outline=outline+'\n'+' '*(open_list_count*4+2)+lines[i]
                    outline=outline[:-1]+' '+lines[i]

                pos=outline.find(style)+offset
                brace_contents=get_substring(outline,pos)
                replacement=brace_contents[offset2:-1]
                if style=='{\\sc' or style=='\\textsc{':replacement=replacement.upper()
                if offset!=0: prefix=style[0:offset]
                else: prefix=''
                if brace_contents[offset2:-1].lstrip()!='': 
                    outline=outline.replace(prefix+brace_contents,markup+replacement.lstrip()+markup+' ')
                else:
                    outline=outline.replace(prefix+brace_contents,'')

        while outline.count('\\cite{'):
            pos=outline.find('\\cite{')+5
            cite_string=get_substring(outline,pos)
            outline=outline.replace('\\cite'+cite_string,"["+cite_string[1:-1]+"]_")
    
        while outline.count('\\Sec{'):
            pos=outline.find('\\Sec{')+4
            cite_string=get_substring(outline,pos)
            outline=outline.replace('\\Sec'+cite_string,":ref:`sec-"+cite_string[1:-1]+"`")
    
        while outline.count('\\Chap{'):
            pos=outline.find('\\Chap{')+5
            cite_string=get_substring(outline,pos)
            outline=outline.replace('\\Chap'+cite_string,":ref:`chap-"+cite_string[1:-1]+"`")
    
        while outline.count('\\Itt{'):
            pos=outline.find('\\Itt{')+4
            index_string=get_substring(outline,pos)
            outline=outline.replace('\\Itt'+index_string,'')

        while outline.count('\\I{'):
            pos=outline.find('\\I{')+2
            index_string=get_substring(outline,pos)
            outline=outline.replace('\\I'+index_string,'')

        #Just delete these things:
        outline=outline.replace('\\noindent','')
        outline=outline.replace('\\newpage','')
        outline=outline.replace('\\newstuff{','')
        outline=outline.replace('\\vskip 25pt','')
        outline=outline.replace('\\vskip 10pt','')
        outline=outline.replace('\\vskip 5pt','')
        outline=outline.replace('\\bsplit','\\begin{split}')
#        outline=outline.replace('\\end{split}','')
        if outline=='}\n': outline='\n'

        if outline!='\n': outline=outline.lstrip()
        if open_list_count and outline!='':
            if outline.count('\\item'):
                if enum==0:
                    outline=' '*(4*open_list_count)+'* '+outline.replace('\\item','').lstrip()
                else:
                    outline=' '*(4*open_list_count)+'#. '+outline.replace('\\item','').lstrip()
                if not in_eqn: 
                    outline=outline.replace('[','',1)
                    outline=outline.replace(']','',1)
            else:
                if enum==0:
                    outline=' '*(4*open_list_count)+'  '+outline
                else:
                    outline=' '*(4*open_list_count)+'   '+outline
        if verbatim: outline='    '+outline

        #Math environments:
        outline=outline.replace('\[','\\\[')
        outline=outline.replace('\]','\\\]')
        outline=outline.replace('$','`')
        outline=outline.replace('`CLAW','\$CLAW')
        outline=outline.replace('`i`th','`i` th')

        if outline.count('http'): outline=outline.replace('``','')

        #Check if a verbatim environment follows, and act accordingly:
#        if i<len(lines)-3: 
#            nextline=lines[i+1]
#            nextnextline=lines[i+2]
#            if (nextline=='\n' and nextnextline.count('\\begin{verbatim}')): i=i+1
#            if nextline.count('\\begin{verbatim}') or (nextline=='\n' and nextnextline.count('\\begin{verbatim}')):
#                if outline[-2]==':':
#                    outline=outline[0:-1]+':\n'
#                else:
#                    outline=outline[0:-1]+'::\n'

        if not outline.count('\\ignore{'): output.write(outline)
        

    input.close()
    output.close()



def macro_tex2jsmath(texfile='RJLmacros',jsfile='out'):
    """
        Convert laTeX macros to jsMath macros.
    """

    input=open(texfile+'.tex','rU')
    output=open(jsfile+'.js','w')

    #First read in the macros
    macrolist=[]
    for line in input:

        if not line.startswith('\\newcommand'): continue
        
        if line[11]=='{':
            short=get_substring(line,11)[2:-1]
            longstart=11+len(short)+3
            if line[longstart]=='{':
                #macro of form \newcommand{\short}{long}
                try:
                    long=get_substring(line,longstart)[1:-1].replace('\\','\\\\')
                    macrolist.append((short,long))
                except: pass
        elif line[11]=='\\':
            short=line[12:line.find('{',12)]
            longstart=11+len(short)+1
            if line[longstart]=='{' and short!='for':
                #macro of form \newcommand\short{long}
                try:
                    long=get_substring(line,longstart)[1:-1].replace('\\','\\\\')
                    macrolist.append((short,long))
                except: pass

    input.close()

    #Now write out the macros
    input=open(jsfile+'_.js','rU')
    output=open(jsfile+'.js','w')

    for line in input:
        output.write(line)
        if line.count('macros:'):
            for short,long in macrolist:
                output.write(' '*10+short+': '+"'"+long+"',\n")

    input.close()
    output.close()
