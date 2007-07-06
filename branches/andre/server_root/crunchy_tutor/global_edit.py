# utility module to make changes accross the crunchy tutorials

import time

files = ["index.html", "interpreter.html", "editor.html",
"doctest.html", "canvas.html", "plot.html", "sound.html", "external.html"]

'''
<a href="index.html">Welcome</a>
<a href="interpreter.html">Interpreter</a>
<a href="editor.html">Editor</a>
<a href="doctest.html">DocTest</a>
<a href="canvas.html">Graphics: drawing</a>
<a href="plot.html">Graphics: plotting</a>
<a href="sound.html">Sound</a>
<a href="external.html">External applications</a>
'''

original = '<a href="images.html">Image files</a>'
replacement = '<a href="images.html">Image files</a>\n<a href="external.html">External applications</a>'

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