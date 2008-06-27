'''
session.py
put session related code in this file 
expose the start_session , get_session  function
'''
import md5
import threading
import time

sessions = {}
#This is experiment. 
#Create a thread-local object to save local datas.
#eg. current session id
thread_data = threading.local()

def start_session(sid = None):
    if not sid or sid not in sessions: #no sid or invalid sid
        sid = md5.md5("%d" % (time.time())).hexdigest()
        sessions[sid] = {}
    thread_data.session_id = sid
    return sid


def get_session():
    sid = thread_data.session_id
    return sessions[sid]


'''
the following is about logging
1. log id 
'''
