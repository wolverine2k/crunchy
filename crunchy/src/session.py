'''
session.py
put session related code in this file 
expose the start_session , get_session  function
'''
import os
import md5
import threading
import time
from datetime import datetime
from src.interface import config

sessions = {}
#This is experiment. 
#Create a thread-local object to save local datas.
#eg. current session id
thread_data = threading.local()

def start_session(sid = None):
    if not sid or sid not in sessions: #no sid or invalid sid
        sid = md5.md5("%d" % (time.time())).hexdigest()
        sessions[sid] = {
            'sid' : sid, 
            'log' : [], 
            'need_log' : {},
            'log_filename' : 
                os.path.join(os.path.expanduser("~"), "crunchy_log_%s_%s.html" %(datetime.now().strftime("%Y%m%d%H%M%S"), sid[:5]))
        }
    thread_data.session_id = sid
    return sid


def get_session_id():
    return thread_data.session_id

def get_session():
    sid = thread_data.session_id
    return sessions[sid]


#logging stuff
'''
NEED UPDATE
the following is about logging
what do we log  ?  page elements which user used , user's input , execution result 
what is session logging ? 
for every session  -> one log file 
    every user action (apply on log-able element) -> one log item  (element_uid, element_type,  input , output) (maybe timestamp)

eventually we could do some kind of replay
start crunchy with reply mode , specfic the logging file , and reply it.

we should also allow the user to turn on/off the logging

-we need a global dict , maybe config.logs = {'session_id' => (log_flag, [log_item])}-
NO. instead we will save the logs in session object

should we organize the code based on  logid ?
'''

def add_log_id(uid, log_id, t):
    ''' vlam_element with uid has a log_id , and it's vlam type is t
    '''
    get_session()['need_log'][uid] = (log_id, t)

def log(uid, content):
    '''log item is (uid, content)
    we can get log_id by access to sesion['need_log'][uid]
    '''
    get_session()['log'].append((uid, content))
    #save_log()

def log_info(uid):
    return get_session()['need_log'].get(uid, None)

def save_log():
    ''' save the log to a proper file 
    1. log file should be in user's home directory, named as crunchy_log_{time_stamp}_{session_id}.html 
    2. about log log format
    '''
    session = get_session()
    log_filename = session['log_filename']
    f = open(log_filename, 'w')
    f.write(begin_html)
    contents = {}
    #re-organazie the log  (uid -> content)
    for item in session['log']:
        if not log_info(item[0]): #don't need log
            continue
        if item[0] not in contents:
            contents[item[0]] = [item[1]]
        else:
            contents[item[0]].append(item[1])
    log_uids= contents.keys()
    def uid_cmp(x, y):
        x1,x2 = x.split(':')
        y1,y2 = y.split(':')
        if x1 == y1:
            return cmp(int(x2), int(y2))
        else:
            return cmp(int(x1), int(y1))
    log_uids.sort(uid_cmp) # sort by uid 
    for uid in log_uids:
        content = contents[uid]
        log_id, vlam_type = log_info(uid)
        f.write("<h2>log_id = %s    <small>(uid=%s, type=%s)</small></h2>"%(log_id, uid, vlam_type))
        #f.write("<h2>log_id = %s </h2>"%(log_id))
        content = "".join(content)
        f.write("<pre>"+content+"</pre>")

    #f.write(str(session['log']))
    #for uid in session['need_log']:
    #    log_id = session[uid][0]
    #    vlam_type = session[uid][1]
    #    f.write("<h2>log_id = %s    <small>(uid=%s, type=%s)</small></h2>"%(log_id, uid, vlam_type))
    #    content = ''.join([item[1] for item in session['log'] if item[0] == log_id])
    #    f.write("<pre>"+content+"</pre>")
    f.write(end_html)
    f.close()


begin_html = """
<html>
<head>
<title>Crunchy Log</title>
<link rel="stylesheet" type="text/css" href="/crunchy.css">
</head>
<body>
<h1>Crunchy Session Log</h1>
<p>In what follows, the log_id is the name given by the tutorial writer
to the element to be logged, the uid is the unique identifier given
to an element on a page by Crunchy.  If the page gets reloaded, uid
will change but not log_id.
</p><p>By convention, original code from the page is styled using the
Crunchy defaults.
</p>
"""
end_html = """
</body>
</html>
"""

