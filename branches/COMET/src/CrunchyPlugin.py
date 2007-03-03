"""The demo crunchy plugin API
"""

class CrunchyPlugin(object):
    def __init__(self):
        self.register()
        
    def register(self):
        raise NotImplementedError