'''
sanitize.py

The purpose of this module is to process html files (that could be malformed)
using a combination of BeautifulSoup and ElementTree and output a "cleaned up"
file based on a given security level.

This script is meant to be run as a standalone module, using Python 2.x.
It is expected to be launched via exec_external_python_version() located
in file_service.py.

The input file name is expected to be in.html, located in Crunchy's temp
directory.  The output file name is out.html, also located in Crunchy's
temp directory.
'''
import os
import src.configuration
import src.security
from src.interface import ElementTree
from src.element_tree import ElementSoup
from src.interface import config

class Page(object):
   url = 'dummy_url'
   is_local = False
   is_remote = True

if 'current_page' not in config:
    page = Page()
else:
    page = config['current_page']

os.chdir(src.configuration.defaults.temp_dir)
infile = open('in.html', 'r')
html = ElementSoup.parse(infile, encoding = 'utf-8')
tree = ElementTree.ElementTree(html)
tree = src.security.remove_unwanted(tree, page)

out = open('out.html', 'w')
tree.write(out)

infile.close()
out.close()