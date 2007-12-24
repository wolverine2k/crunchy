"""Crunchy: serving up interactive Python tutorials

"""
import socket
import webbrowser
#import pychecker.checker

from src.universal import python_version, u_print
required = 2.4
if python_version < required:
    print("Crunchy requires at least Python version %s"%required)
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
    server = http_serve.MyHTTPServer((host, port), http_serve.HTTPRequestHandler)
    pluginloader.init_plugin_system(server)
    if url is None:
        url = 'http://' + host + ':' + str(port) + '/'
    webbrowser.open(url)
    # print this info so that, if the right browser does not open,
    # the user can copy and paste the URL
    u_print('\nCrunchy Server: serving up interactive tutorials at URL ' +
            url + '\n')
    server.still_serving = True
    while server.still_serving:
        server.handle_request()

if __name__ == "__main__":
    run_crunchy()
