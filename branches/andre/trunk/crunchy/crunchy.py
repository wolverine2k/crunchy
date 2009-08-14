"""Crunchy: serving up interactive Python tutorials

"""
from optparse import OptionParser
import os
import socket
try:
    import webbrowser
except:
    print("webbrowser not available")  # in Jython...

import src.interface
REQUIRED = 2.4
if src.interface.python_version < REQUIRED:
    print("Crunchy requires at least Python version %s"%REQUIRED)
    raise SystemExit

if src.interface.python_version < 3:
    from urllib import quote_plus
    from urlparse import urlsplit
else:
    from urllib.parse import quote_plus
    from urllib.parse import urlsplit

import account_manager

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
    # delay importing these until we've parsed the options.
    import src.configuration
    import src.http_serve as http_serve
    import src.pluginloader as pluginloader

    if port is None:
        port = find_port()
    else:
        port = find_port(start=port)
    server = http_serve.MyHTTPServer((host, port),
                                     http_serve.HTTPRequestHandler)

    ## plugins will register possible additional keywords that
    ## configuration.py should have access to, before it is initialized
    pluginloader.init_plugin_system(server)
    src.configuration.init()
    ##

    base_url = 'http://' + host + ':' + str(port)
    if url is None:
        url =  base_url + '/index.html'
    else:
        url = base_url + url
    open_browser(url)
    # print this info so that, if the right browser does not open,
    # the user can copy and paste the URL
    print('\nCrunchy Server: serving up interactive tutorials at URL ' +
            url + '\n')
    server.still_serving = True
    while server.still_serving:
        try:
            server.handle_request()
        except KeyboardInterrupt:
            print("Received Keyboard Interrupt, Quitting...")
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


    ##### NOTE
    # Many options have been commented out as they have not been fully tested
    # since the introduction of user accounts.  In this way, a user that
    # types python crunchy.py --help will not be presented with a lot of
    # untested options.  And note that even some that are not
    # commented out may not work as expected.
    # This will need to be fixed.


    #safe_url_help = """Uses a different start page when starting Crunchy
    #                and treats the site as completely trusted; this means that
    #                nothing (including scripts) is removed from the pages.
    #
    #                Use ONLY if you absolutely trust the site.
    #                Remote files: http://... (example: http://docs.python.org)
    #                Local files: absolute_path.[htm, html, rst, txt, py, pyw]
    #                """
    #interactive_help = """Somewhat equivalent to normal "python -i script.py".
    #                      Ignored if --url is used.
    #                      """
    #username_help = """use to specify a username to use when starting
    #                    Crunchy with a specified url as a start page as this
    #                    bypass the request by the browser for a username.
    #                      """
    #automated_help = """Used when running automated tests to disable request
    #                    for authentication and to prevent security
    #                    advisory confirmation from appearing when launching
    #                    Crunchy."""
    parser.add_option("--url", action="store", type="string", dest="url",
            help=url_help)

    #parser.add_option("--username", action="store", type="string", dest="username",
    #        help=username_help)

    #parser.add_option("--completely_trusted", action="store", type="string",
    #                  dest="safe_url", help=safe_url_help)
    #parser.add_option("--automated", action="store_true",
    #                  dest="automated", help=automated_help)
    #parser.add_option("--i", action="store", type="string", dest="interactive",
    #        help=interactive_help)
    parser.add_option("--port", action="store", type="int", dest="port",
            help="Specifies the port number to try first (default is 8001) ")
    #parser.add_option("-d", "--debug", action="store_true", dest="debug",
    #        help="Enables interactive settings of debug flags "+\
    #             "(useful for developers)")
    #parser.add_option("--debug_ALL", action="store_true", dest="debug_all",
    #        help="Sets ALL the debug flags to True right from the start "+\
    #             "(useful for developers in case of major problems; not fully implemented)")
    parser.add_option("--accounts_file", action="store", type="string",
                      dest="accounts_file",
            help="Selects a user accounts file path different from default (.PASSWD)")
    # a dummy option to get it to work with py2app:
    parser.add_option("-p")
    (options, dummy) = parser.parse_args()
    #if options.debug:
    #    src.interface.debug_flag = True
    #else:
    #    src.interface.debug_flag = False
    #if options.debug_all:
    #    src.interface.debug_flag = True
    #    for key in src.interface.debug:
    #        src.interface.debug[key] = True
    url = None
    src.interface.completely_safe_url = None
    if options.url:
        url = convert_url(options.url)
    #if options.safe_url:
    #    src.interface.completely_safe_url = urlsplit(options.safe_url)[1]
    #    url = convert_url(options.safe_url)
    #elif options.interactive:
    #    src.interface.interactive = True
    #    url = convert_url(options.interactive)
    #if options.username:
    #    src.interface.username_at_start = options.username
    #if options.automated:
    #    src.interface.config['initial_security_set'] = True
    #    src.interface.config['automated'] = True
    port = None
    if options.port:
        port = options.port
    if options.accounts_file:
        if os.path.exists(options.accounts_file):
            src.interface.accounts = account_manager.Accounts(
                                                          options.accounts_file)
    else:
        src.interface.accounts = account_manager.Accounts()
    return url, port

def convert_url(url):
    '''converts a url into a form used by Crunchy'''
    if src.interface.interactive:
        if 'py' in url.split('.')[-1]:
            url = "/py?url=%s" %  quote_plus(url)
            return url
        else:
            print("invalid file type for --i option.")
            raise SystemExit
    if url.startswith("http:"):
        url = "/remote?url=%s" % quote_plus(url)
    elif os.path.exists(url):
        if 'htm' in url.split('.')[-1]:
            url = "/local?url=%s" % quote_plus(url)
        elif url.split('.')[-1] in ['rst', 'txt']:
            url = "/rst?url=%s" %  quote_plus(url)
        elif 'py' in url.split('.')[-1]:
            url = "/py?url=%s" %  quote_plus(url)
        else:
            print("unknown url file type")
            raise SystemExit
    else:
        print("url specified can not be found.")
        raise SystemExit
    return url

def open_browser(url):
    """
    Open the browser. This function does its best to open firefox.
    """
    try:
        client = webbrowser.get("firefox")
        client.open(url)
        return
    except:
        try:
            client = webbrowser.get()
            client.open(url)
            return
        except:
            print('Please open %s in Mozilla Firefox.' % url)

if __name__ == "__main__":
    _url, _port = parse_options()
    run_crunchy(port=_port, url=_url)
