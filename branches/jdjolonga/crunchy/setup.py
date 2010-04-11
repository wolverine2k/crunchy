"""
:Description: crunchy setup script
:Author: Josip Djolonga, j.djolonga@jacobs-university.de
"""

from setuptools import setup, find_packages

# Note: also see the files included by MANIFEST.in

setup(name='crunchy',
      author = 'Andre Roberge',
      version = '1.1.2',
      packages=find_packages('.'),
      scripts=['scripts/crunchy-server.py',
               'scripts/crunchy-config.py',
               'scripts/crunchy-crst2s5.py'
               ],
      install_requires = ['pygments'],
      include_package_data = True,
)

