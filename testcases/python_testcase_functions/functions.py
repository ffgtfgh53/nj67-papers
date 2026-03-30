class NoMoreClosingFunction():
    "Wrapper which turns obj.close to lambda and hides object behind ._obj"
    def __init__(self, obj):
        self._obj = obj
    
    def __getattr__(self, name):
        if name == 'close':
            return lambda: None
        return getattr(self._obj, name)
    def __enter__(self, *args, **kwargs):
        # Don't check arguments of open()
        return self._obj.__enter__()
    def __exit__(self, *args):
        pass