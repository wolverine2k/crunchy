# utility module to make changes accross the crunchy tutorials

import time

files = ["welcome_en.html", "interpreter_en.html", "editor_en.html",
"doctest_en.html", "canvas_en.html", "writing_en.html", "remote_en.html",
"external_en.html", "images_en.html", "config_en.html"]

original = '<a href="welcome_en.html">Welcome</a>'
replacement = '<a href="welcome_en.html">Begin tutorial</a>'

for f in files:
    inp = open(f, "r")
    lines = inp.readlines()
    inp.close()
    new_lines = []
    for line in lines:
        if original in line:
            line = line.replace(original, replacement)
        if line:
            new_lines.append(line)
    out = open(f, "w")
    full_text = ''.join(new_lines)
    out.write(full_text)
    out.close()
    print "processed file %s"%f

time.sleep(3)  # so we see that it's been done...