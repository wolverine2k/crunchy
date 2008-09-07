'''
Simple utility to create template pages that have the appropriate
sub-menu open.

Run this file anytime there are some changes to the menu included in index.html
in the server_root directory.
'''
import os

cwd = os.getcwd()
os.chdir(os.path.normpath(os.path.join(cwd, "..", "server_root")))
cwd = os.getcwd()
main_template = open("index.html").read()

# The main template has the menu open for the basic tutorial.  So, we just
# make a copy of it in that directory.
local_template = open(os.path.join(cwd, "docs", "basic_tutorial",
                                   "local_template.html"), "w")
local_template.write(main_template)
local_template.close()

# for the other templates, we need to have the menu open at the
# appropriate leval.
main_template = main_template.replace("heading open", "heading")

all = [ ('heading">Advanced', 'heading open ">Advanced', "advanced_tutorial"),
        ('heading">Writing', 'heading open">Writing', "writing"),
        ('heading">About', 'heading open">About', 'about'),
        ('heading">For', 'heading open">For', 'developers'),
        ('heading">Experimental', 'heading open">Experimental', 'experimental'),
        ('heading">Miscellaneous', 'heading open">Miscellaneous', 'misc')]

for info in all:
    local_template = open(os.path.join(cwd, "docs", info[2],
                                   "local_template.html"), "w")
    new_text = main_template.replace(info[0], info[1])
    local_template.write(new_text)
    local_template.close()
