"""Crunchy: serving up interactive Python tutorials

"""
from optparse import OptionParser
import socket
import urllib
import webbrowser

import src.interface
REQUIRED = 2.4
if src.interface.python_version < REQUIRED:
    print("Crunchy requires at least Python version %s"%REQUIRED)
    raise SystemExit

def find_port(start=8001):
    """finds the first free port on 127.0.0.1 starting at start"""
    finalport = None
    testsock = socket.socket()
    testn = start
    while not finalport and (testn < 65536):
        try:
            testsock.bind(('127.0.0.1', testn))
            finalport = testn
        except socket.error:
            testn += 1
    testsock.close()
    return finalport

def run_crunchy(host='127.0.0.1', port=None, url=None):
    '''starts Crunchy

    * set the port to the value specified, or looks for a free one
    * open a web browser at given url, or a default if not specified
    '''
    ## keep the following import inside this function so that
    ## we can run unit tests using Python 3.0
    import src.http_serve as http_serve
    import src.pluginloader as pluginloader
    if port is None:
        port = find_port()
    else:
        port = find_port(start=port)
    server = http_serve.MyHTTPServer((host, port),
                                     http_serve.HTTPRequestHandler)
    pluginloader.init_plugin_system(server)
    base_url = 'http://' + host + ':' + str(port)
    if url is None:
        url =  base_url + '/'
    else:
        url = base_url + url
    webbrowser.open(url)
    # print this info so that, if the right browser does not open,
    # the user can copy and paste the URL
    print('\nCrunchy Server: serving up interactive tutorials at URL ' +
            url + '\n')
    server.still_serving = True
    while server.still_serving:
        server.handle_request()

usage = '''python crunchy.py [options]

If your browser does not start or does not open a new tab on its own,
or you have a non-supported browser that starts instead, start Firefox and copy
the url displayed in the terminal that appeared when you launched Crunchy into
the address bar (that's the white rectangular box at the top
of your browser that contains stuff like [http:// ...]).
The url to be copied there should be something like:
http://127.0.0.1:8002/
Copy this in and press enter - Crunchy's first page should be displayed.'''

def parse_options():
    '''parse command line options'''
    parser = OptionParser(usage)
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
            help="Enables interactive settings of debug flags "+\
                 "(useful for developers)")
    parser.add_option("--debug_ALL", action="store_true", dest="debug_all",
            help="Sets ALL the debug flags to True right from the start "+\
                 "(useful for developers in case of major problems)")
    parser.add_option("--url", action="store", type="string", dest="url",
            help="Uses a different start page (not implemented yet) ")
    parser.add_option("--port", action="store", type="int", dest="port",
            help="Specifies the port number to try first (default is 8001) ")
    (options, args) = parser.parse_args()
    if options.debug:
        src.interface.debug_flag = True
    else:
        src.interface.debug_flag = False
    if options.debug_all:
        src.interface.debug_flag = True
        for key in src.interface.debug:
            src.interface.debug[key] = True
    url = None
    if options.url:
        url = convert_url(options.url)
    port = None
    if options.port:
        port = options.port
    return url, port

def convert_url(url):
    '''converts a url into a form used by Crunchy'''
    if url.startswith("http:"):
        url = "/remote?url=%s" % urllib.quote_plus(url)
        print url
    return url

if __name__ == "__main__":
    url, port = parse_options()
    run_crunchy(port=port, url=url)
