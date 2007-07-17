from distutils.core import setup
import glob
import py2exe

import sys
import os

# write all_plugins.py -- contains an import for each plugin.py file
# this is included so that py2exe knows which modules are required by the plugins
f = open("all_plugins.py", "w")
pluginpath = "src\\plugins"
pluginfiles = [x[:-3] for x in os.listdir(pluginpath) if x.endswith(".py")]
for p in pluginfiles:
    f.write("import src.plugins." + p + "\n")
f.close()

setup(console=["crunchy.py"],
      data_files=[("server_root", glob.glob("server_root\\*.*")),
                  ("server_root/crunchy_tutor", glob.glob("server_root\\crunchy_tutor\\*.*")),
                  ("server_root/edit_area", glob.glob("server_root\\edit_area\\*.*")),
                  ("server_root/edit_area/images", glob.glob("server_root\\edit_area\\images\\*.*")),
                  ("server_root/edit_area/langs", glob.glob("server_root\\edit_area\\langs\\*.*")),
                  ("server_root/edit_area/reg_syntax", glob.glob("server_root\\edit_area\\reg_syntax\\*.*")),
                  ("server_root/functional_tests", glob.glob("server_root\\functional_tests\\*.*")),
                  ("server_root/functional_tests/sub_directory", glob.glob("server_root\\functional_tests\\sub_directory\\*.*")),
                  ("server_root/functional_tests/sub_directory/sub2", glob.glob("server_root\\functional_tests\\sub_directory\\sub2\\*.*")),
                  ("translations", glob.glob("translations\\*.*")),
                  ("translations/de/LC_MESSAGES", glob.glob("translations\\de\\LC_MESSAGES\\*.*")),
                  ("translations/en/LC_MESSAGES", glob.glob("translations\\en\\LC_MESSAGES\\*.*")),
                  ("translations/en_GB/LC_MESSAGES", glob.glob("translations\\en_GB\\LC_MESSAGES\\*.*")),
                  ("translations/fr/LC_MESSAGES", glob.glob("translations\\fr\\LC_MESSAGES\\*.*")),
                  ("src", glob.glob("src\\*.*")),
                  ("src/plugins", glob.glob("src\\plugins\\*.*"))]
)

os.remove("all_plugins.py")

# TODO: Write the win32 release script in Python rather than a windows batch file
#import shutil
#shutil.copytree ("dist", "..\\..\\release\\win32")
#shutil.rmtree ("dist", True)
#shutil.rmtree ("build", True)