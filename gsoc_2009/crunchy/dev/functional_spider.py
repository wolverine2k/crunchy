import logging
log = logging.getLogger(__name__)

import os
import re
import sys
import urllib2
import urlparse
from optparse import OptionParser
from StringIO import StringIO

def find_src():
    """Finds where the Crunchy src module lives."""

    path = os.path.abspath(__file__)
    path = os.path.dirname(path)
    path = os.path.dirname(path)
    sys.path.insert(0, path)

find_src()
from src.interface import ElementTree as ET

BLURB = """
I am a spider that recurses through the anchor hrefs of two Crunchy
websites looking for differences betwen the two websites. This is
especially useful in comparing two version of Crunchy, one running on
Python 2 and the other on Python 3. Any differences or server
tracebacks are logged to console. 404 and 500 errors are generated as
exceptions by urllib2 for now. I am intelligent enough to normalize
the HTML through a series of regular expressions that strip out
session-specific identifiers. I use ElementTree to parse the HTML and
extract anchor hrefs.

To use, first run the two Crunchy servers; for example, "python2
/path/to/left/crunchy.py --port=8002" and "python3
/path/to/right/crunchy.py --port=8003". Each of these Crunchy
instances must have a pristine account set up under the name
"tools-spider" with the password "tools-spider". It is of crucial
importance that these accounts are pristine as otherwise differences
due to different preferences may arise.

Then, you would run me with "python functional_spider localhost:8002
localhost:8003". We designate localhost:8002 and localhost:8003
respectively as "left" and "right". Links are visited first on the
left website, whose output is compared with the corresponding right
website.

If you are debugging this script, the best way to find out why two
websites are different is to copy and paste the cannibalize function
into another script, run it on two files, write the two outputs to two
temp files, and use wdiff to compare the two files. You have to use
wdiff because cannibalize strips out all newlines, which in turn is
because ElementTree produces different whitespacing between Python 2
and 3.
""".strip()

NS_XHTML = "http://www.w3.org/1999/xhtml"

R_NEWLINES = re.compile(r'[\r\n]')
R_ABSURLS = re.compile(r'http://.*?/')
R_KEYS = re.compile(r'\d+?_\d+')
R_LONGKEYS = re.compile(r'\d{4,}')
R_PYTHON = re.compile(r'python\d')
R_PYTHONVER = re.compile(r'\(Python version .*?\)')
R_JQUERY = re.compile(r'jquery_\d+')
R_RUNOUTPUT = re.compile(r'runOutput\(.*?\)')
R_CONSOLES = re.compile(r'Console\(.*?\)')
R_EXIT = re.compile(r'exit\d+')

def cannibalize(text):
    """Normalizes the text in different Crunchy websites by stripping
    out any session-specific identifiers."""

    text = R_NEWLINES.sub('', text)
    text = R_ABSURLS.sub('/', text)
    text = R_KEYS.sub('', text)
    text = R_LONGKEYS.sub('', text)
    text = R_PYTHON.sub('python', text)
    text = R_PYTHONVER.sub('(Python version)', text)
    text = R_JQUERY.sub('jquery', text)
    text = R_RUNOUTPUT.sub('runOutput', text)
    text = R_CONSOLES.sub('Console', text)
    text = R_EXIT.sub('exit', text)
    return text

class Tree(object):
    """Wrapper over ElementTree for a Crunchy page."""

    def __init__(self, handle):
        """Takes a handle producing UTF-8 encoded bytestrings. Raises
        UnicodeDecodeError if otherwise occurs. Closes the handle."""

        self.tree = ET.parse(StringIO(handle.read().decode('utf8')))
        handle.close()

    def hrefs(self, via):
        """Returns a list of URLs, resolving relative addresses using
        the via argument, pointed to by anchors."""

        anchors = self.tree.findall(".//{%s}a" % NS_XHTML)
        def helper():
            for anchor in anchors:
                href = anchor.attrib.get('href')

                # Some anchors exist purely for JavaScript.
                if not href: continue
                # Some anchors lead to external websites.
                if not href.endswith('.html'): continue
                if '/remote' in href: continue

                yield urlparse.urljoin(via, href)

        return list(helper())

class Spider(object):
    """A Crunchy web page spider for checking the output in Python 2
    and Python 3 given the credentials and location for both
    websites."""

    def __init__(self, python2, python3):
        self.opener2 = self.create_opener(*python2)
        self.opener3 = self.create_opener(*python3)

    def create_opener(self, host, user, passwd):
        """Returns an urllib2 opener and the root of the website."""

        handler = urllib2.HTTPDigestAuthHandler()
        uri = 'http://%s/' % host
        handler.add_password(realm='Crunchy Access',
                             uri=uri,
                             user=user,
                             passwd=passwd)

        opener = urllib2.build_opener(handler)
        # Monkeypatch the opener object.
        opener.host = host
        opener.root = uri
        return opener

    def open2(self, url):
        """A url opener appropriate for self.slurp. Returns a urllib2
        file-like object given the absolute url without the host or
        port information e.g. / or /index.html."""

        return self.opener2.open(url)

    def open3(self, url):
        """A url opener appropriate for self.slurp. Returns a urllib2
        file-like object given the absolute url without the host or
        port information e.g. / or /index.html."""

        # Convert any URL into the Crunchy Python 3 website equivalent.
        o = urlparse.urlparse(url)
        url = urlparse.urlunparse((o.scheme,
                                   self.opener3.host,
                                   o.path,
                                   o.params,
                                   o.query,
                                   o.fragment))
        return self.opener3.open(url)

    def slurp(self, url, opener):
        """Returns the cannibalized contents of the url on the Python
        2 Crunchy website given a url opener."""

        h = opener(url)
        text = h.read().decode('utf8')
        h.close()

        text = cannibalize(text)
        return text

    def run(self):
        """Runs a breadth-first spider on the Python 2 Crunchy
        website, checking contents against the Python 3."""

        # BFS stack of nodes.
        stack = [self.opener2.root]
        # Visited nodes; never visit again.
        visited = set()

        while len(stack):
            url  = stack.pop(0)
            if url in visited:
                continue
            log.info('Visting: %s' % url)

            tree = Tree(self.open2(url))
            x2 = self.slurp(url, self.open2)
            x3 = self.slurp(url, self.open3)

            if not x2 == x3:
                log.error('Different: %s' % url)

            # A semi-reliable way of detecting whether a traceback has
            # occurred or not by piggybacking the output of
            # handle_default.py. Tracebacks that fall through
            # handle_default.py become 500 server errors, which in
            # turn become urllib2.HTTPError exceptions that we don't
            # handle as this point.
            if 'Please file a bug report' in x2:
                log.error('Traceback: %s' % url)

            visited.add(url)
            stack.extend(tree.hrefs(via=url))

def main():
    """The spidering script."""

    usage  = "usage: %prog [options] host[:port] host[:port]\n\n" + BLURB
    parser = OptionParser(usage=usage)
    parser.add_option('-v', '--verbose', dest='verbose',
                      help='Be verbose',
                      action='store_true')

    options, args = parser.parse_args()

    # Set up logging first. ####################
    handler = logging.StreamHandler()
    log.addHandler(handler)

    if options.verbose:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARNING)

    # On to the show. ####################
    s = Spider((args[0], 'tools-spider', 'tools-spider'),
               (args[1], 'tools-spider', 'tools-spider'))
    s.run()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Keyboard interrupted, goodbye!')
    except urllib2.URLError, e:
        print('Error: One or both of the websites passed were unaccessible or became unaccessible. Recheck that you have inputted the correct information and consult the Crunchy server logs.')
