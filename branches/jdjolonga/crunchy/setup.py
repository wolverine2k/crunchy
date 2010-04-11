from setuptools import setup, find_packages

setup(name='crunchy',
      author = 'Andre Roberge',
      version = '1.1.2',
      packages=find_packages('.'),
      scripts=['scripts/crunchy-server.py',
               'scripts/crunchy-config.py',
               'scripts/crunchy-crst2s5.py'
               ],
      include_package_data = True,
)

