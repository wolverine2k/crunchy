'''exam_mode.py

'''
import time
import sys

from src.interface import StringIO, plugin, config, Element, SubElement,exams
from src.utilities import parse_vlam
from src import session


def register():
    """The register() function is required for all plugins.
       In this case, we need to register two types of 'actions':
       1. three custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup.
       2. a custom http handler to deal with "run doctest" commands,
          issued by clicking on a button incorporated in the
          'doctest widget';
       """
    # 'doctest' only appears inside <pre> elements, using the notation
    # <pre title='doctest ...'>
    plugin['register_tag_handler']("pre", "title", "exam_define",
                                          setup_exam)
    #plugin['register_http_handler']("/check_code", doc_code_check_callback)


def setup_exam(page, elem, uid):
    global exams
    vlam = elem.attrib['title']
    vlam_info = parse_vlam(vlam)
    if 'name' not in vlam_info or 'start' not in vlam_info or 'durations' not in vlam_info:
        print vlam_info
        print "not a valid exam"
        return
    else:
        exam_name = vlam_info['name']
        now = time.time()
        start_time_tuple = time.strptime(vlam_info['start'],'%Y-%m-%d_%X')
        start_time = time.mktime(start_time_tuple)
        print time.strftime('%Y-%m-%d %X', time.localtime(now))
        if now < start_time:
            elem.text = "Exam not started . It will start at " + vlam_info['name']
            return 
        elif now > start_time + 60 * int(vlam_info['durations'][:-1]):
            elem.text = "Exam has been finished. You are late . It was start at %s  and last %s minutes" %(
                    time.strftime('%Y-%m-%d %X',start_time_tuple), vlam_info['durations'][:-1])
            return
        if exam_name in exams:
            return
        else:
            exams[exam_name] = vlam_info  
            exams[exam_name]['problems'] = []
            elem.text = "Exam %s , start at %s (Durations : %s minutes) " %(
                    exam_name, time.strftime('%Y-%m-%d %X',start_time_tuple), vlam_info['durations'][:-1])


