'''
Extract Python file information for keeping track of dependecies and
testing status

'''

import os.path

info = {}
OFFSET = '    '
functions_tested = 0
functions_total = 0
nb_files = 0

def visit(arg, dirname, names):
    new_dir = {}
    new_dir['name'] = dirname
    new_dir['python_files'] = []
    info[dirname] = new_dir
    # Do not recurse into .svn directory
    if '.svn' in names:
        names.remove('.svn')
    if 'element_tree' in names:
        names.remove('element_tree')
    for name in names:
        subname = os.path.join(dirname, name)
        # only include Python files
        if subname.endswith('.py'):
            new_dir['python_files'].append(name)

def changeHTMLspecialCharacters(text):
    '''replace <>& by their escaped valued so they are displayed properly
       in browser.'''
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

def extract_lines(filename):
    ''' extract lines with relevant information

    - lines showing modules imported
    - lines with class definitions
    - lines with function/methods definitions
    - lines with plugin registration [inside register() if present]
    '''
    global functions_total, functions_tested
    functions = []
    lines = open(filename).readlines()
    close_paren = True
    inside_register = False

    for line in lines:
        if not close_paren:
            functions.append(line[:-1].replace(':', ''))  # remove trailing new line
            if ')' in line:
                close_paren = True

        # extract lines with imports
        if line.strip().startswith('import ') or (
            line.strip().startswith('from ') and ' import ' in line):
            text = changeHTMLspecialCharacters(line[:-1])
            functions.append(text)

        # extract lines with class definitions
        if line.strip().startswith('class '):
            inside_register = False
            text = changeHTMLspecialCharacters(line[:-1])
            functions.append(text)
            if ')' not in line:
                close_paren = False

        # extract lines with function or method definitions
        if line.strip().startswith('def '):
            text = changeHTMLspecialCharacters(line[:-1])
            if 'register()' in line:
                inside_register = True
                text = text.replace('def ', '')
            else:
                inside_register = False
                text = text.replace('def ', '').replace(':', '')
            functions.append(text)
            if ')' not in line:
                close_paren = False
            functions_total += 1
            if 'tested' in line:
                functions_tested += 1

        # extract lines with plugin information
        if line.strip().startswith('plugin[') and inside_register:
            text = changeHTMLspecialCharacters(line[:-1])
            text = OFFSET + text.strip()  # hack to keep indentation right
            functions.append(text)
            if ')' not in line:
                close_paren = False
    return functions


os.path.walk('../crunchy/', visit, info)

begin_file = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<title>Dependencies and test status</title>
</head>
<body>
<h1>Tree structure, classes and methods or functions, and test status</h1>
<p>
The following information is generated from the sources.
Please run test_status.py to get the latest.
Note that the test information is only as good as it has been
documented in the source files.  Try to help in keeping this up to date.
</p>
<pre title="python_code">
'''

end_file = '''
</pre>
</body></html>
'''

filename = "../crunchy/server_root/test_status.html"
report = open(filename,'w')
report.write(begin_file)

for dirname in info:
    if info[dirname]['python_files']:
        report.write(info[dirname]['name'].replace('../', '') + '\n')
        for filename in info[dirname]['python_files']:
            nb_files += 1
            report.write(OFFSET + filename + '\n')
            full_path = os.path.join(info[dirname]['name'], filename)
            lines = extract_lines(full_path)
            for line in lines:
                report.write(2*OFFSET + line + '\n')

report.write(end_file)
report.close()
print "total number of Python files: ", nb_files
print "-----------------------------------------"
print "total number of functions/methods: ", functions_total
print "total number tested: ", functions_tested
