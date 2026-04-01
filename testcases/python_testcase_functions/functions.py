import io

from typing import Any

class NoMoreClosingFunction():
    """
    Wrapper around io.StringIO which removes .close() and .__exit__() methods

    Useful for returning a StringIO to a patched function which we can access later after function exits
    """
    def __init__(self, obj: Any=io.StringIO):
        self._obj = obj
    
    def __getattr__(self, name):
        if name == 'close':
            return lambda: None
        return getattr(self._obj, name)
    def __enter__(self, *args, **kwargs):
        # Don't check arguments of open(), they should have been check in self.mock_open()
        return self._obj.__enter__()
    def __exit__(self, exc_type, exc_value, traceback):
        pass