"""Crunchy: serving up interactive Python tutorials

"""
from optparse import OptionParser
import os,sys
import socket
import urllib
from urlparse import urlsplit
import webbrowser

import src.account_manager

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
        try:
            server.handle_request()
        except KeyboardInterrupt:
            print("Recieved Keyboard Interrupt, Quitting...")
            server.still_serving = False
    server.server_close()

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
    url_help = """Uses a different start page when starting Crunchy
                    Remote files: http://... (example: http://docs.python.org)
                    Local files: absolute_path.[htm, html, rst, txt, py, pyw]
                """
    safe_url_help = """Uses a different start page when starting Crunchy
                    and treats the site as completely trusted; this means that
                    nothing (including scripts) is removed from the pages.

                    Use ONLY if you absolutely trust the site.
                    Remote files: http://... (example: http://docs.python.org)
                    Local files: absolute_path.[htm, html, rst, txt, py, pyw]
                    """
    interactive_help = """Somewhat equivalent to normal "python -i script.py".
                          Ignored if --url is used.
                          """
    automated_help = """Used when running automated tests to prevent security
                        advisory confirmation from appearing when launching
                        Crunchy."""
    parser.add_option("--url", action="store", type="string", dest="url",
            help=url_help)
    parser.add_option("--completely_trusted", action="store", type="string",
                      dest="safe_url", help=safe_url_help)
    parser.add_option("--automated", action="store", type="string",
                      dest="automated", help=automated_help)
    parser.add_option("--i", action="store", type="string", dest="interactive",
            help=interactive_help)
    parser.add_option("--port", action="store", type="int", dest="port",
            help="Specifies the port number to try first (default is 8001) ")
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
            help="Enables interactive settings of debug flags "+\
                 "(useful for developers)")
    parser.add_option("--debug_ALL", action="store_true", dest="debug_all",
            help="Sets ALL the debug flags to True right from the start "+\
                 "(useful for developers in case of major problems; not fully implemented)")
    parser.add_option("--server_mode", action="store_true", dest="server_mode",
            help="Start crunchy in server mode.")
   # a dummy option to get it to work with py2app:
    parser.add_option("-p")
    (options, dummy) = parser.parse_args()
    if options.debug:
        src.interface.debug_flag = True
    else:
        src.interface.debug_flag = False
    if options.debug_all:
        src.interface.debug_flag = True
        for key in src.interface.debug:
            src.interface.debug[key] = True
    #we are in server mode
    #we have to ask for a  master password 
    #if passwd file not exist , ask user to create one using account manager.
    if options.server_mode:
        src.interface.server_mode = True
        accounts = {}
        if not check_for_password_file():
            am = src.account_manager.AMCLI()
            try:
                am.start()
            except SystemExit,e:#exit from account manager
                if len(am.accounts) == 0:
                    print("no valid user account")
                    raise SystemExit
                else:
                    accounts = am.accounts
        else:
            accounts = src.account_manager.get_accounts()
        src.interface.accounts = accounts
    else:
        src.interface.server_mode = False

    url = None
    src.interface.completely_safe_url = None
    if options.url:
        url = convert_url(options.url)
    if options.safe_url:
        src.interface.completely_safe_url = urlsplit(options.safe_url)[1]
        url = convert_url(options.safe_url)
    elif options.interactive:
        src.interface.interactive = True
        url = convert_url(options.interactive)
    if options.automated:
        src.interface.config['initial_security_set'] = True
    port = None
    if options.port:
        port = options.port
    return url, port

def convert_url(url):
    '''converts a url into a form used by Crunchy'''
    if src.interface.interactive:
        if 'py' in url.split('.')[-1]:
            url = "/py?url=%s" %  urllib.quote_plus(url)
            return url
        else:
            print("invalid file type for --i option.")
            raise SystemExit
    if url.startswith("http:"):
        url = "/remote?url=%s" % urllib.quote_plus(url)
    elif os.path.exists(url):
        if 'htm' in url.split('.')[-1]:
            url = "/local?url=%s" % urllib.quote_plus(url)
        elif url.split('.')[-1] in ['rst', 'txt']:
            url = "/rst?url=%s" %  urllib.quote_plus(url)
        elif 'py' in url.split('.')[-1]:
            url = "/py?url=%s" %  urllib.quote_plus(url)
        else:
            print("unknown url file type")
            raise SystemExit
    else:
        print("url specified can not be found.")
        raise SystemExit
    return url

def check_for_password_file():
    pwd_file_path = os.path.join(os.getcwd(), '.PASSWD') 
    if not os.path.exists(pwd_file_path):
        print("Password file not exisi, please create one using the accout manager")
        return False
    else:
        return True

if __name__ == "__main__":
    _url, _port = parse_options()
    run_crunchy(port=_port, url=_url)
