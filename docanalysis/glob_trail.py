import os
from glob import glob
from pprint import pprint

# define constants
ABS = ['*abstract.xml']
ACK = ['*ack.xml']
AFF = ['*aff.xml']
AUT = ['*contrib-group.xml']
CON = ['*conclusion*/*.xml']
DIS = ['*discussion*/**/*_title.xml', '*discussion*/**/*_p.xml'] # might bring unwanted sections like tables, fig. captions etc. Maybe get only title and paragraphs?
ETH = ['*ethic*/*.xml']
FIG = ['*fig*.xml']
INT = ['*introduction*/*.xml', '*background*/*.xml']
KEY = ['*kwd-group.xml']
MET = ['*method*/*.xml', '*material*/*.xml'] # also gets us supplementary material. Not sure how to exclude them
RES = ['*result*/*/*_title.xml', '*result*/*/*_p.xml'] # not sure if we should use recursive globbing or not. 
TAB = ['*table*.xml']
TIL = ['*article-meta/*title-group.xml']

# glob
path = os.getcwd()
cproj = 'corpus/asp_nat_products'
LIST_SEC = [TIL, KEY]
for SEC in LIST_SEC:
    for opt in SEC:
        glob_list=glob(os.path.join(path, cproj, '**', 'sections', '**', f'{opt}'), recursive=True)
        pprint(glob_list)

# Section list comes from: https://github.com/petermr/pyami/blob/main/py4ami/resources/section_templates.json