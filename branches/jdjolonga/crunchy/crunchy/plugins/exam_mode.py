'''exam_mode.py

'''
import time

from crunchy.interface import plugin, exams
from crunchy.utilities import parse_vlam

def register():
    """The register() function is required for all plugins.
       """
    plugin['register_tag_handler']("pre", "title", "exam_define",
                                          setup_exam)

def setup_exam(page, elem, dummy_uid):
    vlam = elem.attrib['title']
    vlam_info = parse_vlam(vlam)
    exam_name = vlam_info['name']
    if 'name' not in vlam_info or 'start' not in vlam_info or 'duration' not in vlam_info:
        print(vlam_info)
        print("not a valid exam")
        return
    else:
        now = time.time()
        start_time_tuple = time.strptime(vlam_info['start'],'%Y-%m-%d_%X')
        start_time = time.mktime(start_time_tuple)
        #print time.strftime('%Y-%m-%d %X', time.localtime(now))
        now_str = time.strftime('%Y-%m-%d %X', time.localtime(now))
        start_str = time.strftime('%Y-%m-%d %X', time.localtime(start_time))
        if now < start_time:
            elem.text = """It is %s. The exam is not started.
It will start at %s""" % (now_str, start_str)
            # the following test should not be needed in production code
            # as the exam would not have yet been created.  However, we should
            # keep it as it is useful for testing - editing the html page,
            # changing time to see if the exam is allowed to take place or not.
            if page.username in exams:
                if exam_name in exams[page.username]:
                    del exams[page.username][exam_name]
            return
        elif now > start_time + 60 * int(vlam_info['duration'][:-1]):
            elem.text = """Sorry, the time to complete the exam is over.
It was started at %s and lasted %s minutes.""" % (
                    time.strftime('%Y-%m-%d %X',start_time_tuple), vlam_info['duration'][:-1])
            if page.username in exams:
                if exam_name in exams[page.username]:
                    del exams[page.username][exam_name]
            return
        # record the exam name which is in progress
        if page.username not in exams:
            exams[page.username] = {}
        if exam_name not in exams[page.username]:
            exams[page.username][exam_name] = {}
        exams[page.username][exam_name]['problems'] = []
        elem.text = "The Exam %s, started at %s (Duration: %s minutes.)\n" % (
                exam_name, time.strftime('%Y-%m-%d %X',start_time_tuple),
                vlam_info['duration'][:-1])
        elem.text += "It is currently %s." % now_str
