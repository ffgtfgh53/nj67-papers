"""Yo just saying this was fully AI Generated with 10% manual user editing (ok >30% now)

DOES NOT WORK ON PYTHON 3.8 but works on 3.11 (idk why, some behavior changed ig)"""
from __future__ import annotations # atp idk what this is supporting if even 3.8 not supported

from unittest.mock import patch, MagicMock
from contextlib import ExitStack
from warnings import deprecated

@deprecated("SecureTest is depreciated and will be replaces by load_user_functions (using RestrictedPython)")
class SecureTest:
    """\
    Class decorator that patches dangerous functions for testing untrusted code.
    
    It is possible to specify additional functions to leave unpatched, but then it is your responsibility to ensure that these functions are patched when running user code.
    (e.g. when you want to save the result of a file write)

    There are also some convenient subclasses that also unpatch common functions, like `SecureTestWithFileOpen` for `builtins.open`

    Example usage:
    ```
    @SecureTest(additional_modules=['sqlite3'])
    class TestDummy(unittest.TestCase):
        def test_dummy(self):
            import sqlite3 # Ok
            import sys # PermissionError
    ```
    """
    
    DANGEROUS_FUNCTIONS = {
        # File system
        'builtins.open':            PermissionError("File access denied"),
        'os.remove':                PermissionError("Delete denied"),
        'os.rmdir':                 PermissionError("Delete denied"),
        'os.unlink':                PermissionError("Delete denied"),
        'shutil.rmtree':            PermissionError("Delete denied"),
        'pathlib.Path.unlink':      PermissionError("Delete denied"),
        'pathlib.Path.write_text':  PermissionError("Write denied"),
        'pathlib.Path.write_bytes': PermissionError("Write denied"),

        # Network
        'socket.socket':              PermissionError("Network access denied"),
        'socket.create_connection':   PermissionError("Network access denied"),
        # 'requests.get':             PermissionError("Network access denied"),
        # 'requests.post':            PermissionError("Network access denied"),
        # 'requests.put':             PermissionError("Network access denied"),
        # 'requests.delete':          PermissionError("Network access denied"), # somehow uncommenting leads to a bunch of ModuleNotFoundError
        'urllib.request.urlopen':     PermissionError("Network access denied"),
        'http.client.HTTPConnection': PermissionError("Network access denied"),
        
        # Execution
        'subprocess.run':   PermissionError("Execution denied"),
        'subprocess.Popen': PermissionError("Execution denied"),
        'subprocess.call':  PermissionError("Execution denied"),
        'os.system':        PermissionError("Execution denied"),
        'os.popen':         PermissionError("Execution denied"),
        'builtins.eval':    PermissionError("Execution denied"),
        'builtins.exec':    PermissionError("Execution denied"),
        'builtins.compile': PermissionError("Compilation denied"),
    }
    
    # Safe modules that untrusted code can import
    DEFAULT_SAFE_MODULES = {
        'math', 'json', 'datetime', 'time', 'uuid', 'hashlib',
        'collections', 'itertools', 're', 'string', 'random',
        'statistics', 'decimal', 'fractions', 'array', 'csv', 
        'base64', 'codecs', 'functools', 'operator', 'types',
        #cpython modules
        '_colorize', '__hello__'
    }
    
    def __init__(self, additional_modules:list[str]=[], additional_builtins:list[str]=[], allowed_functions:list[str]=[],
                 block_environment:bool=True, block_globals:bool=True):
        """\
        Args:
            additional_modules: List of module names untrusted code can import in addition to default
            additional_builtins: List of safe builtins to allow in addition to default
            block_environment: If True, clear os.environ
            block_globals: If True, block access to globals()
        """
        self.allowed_modules = self.DEFAULT_SAFE_MODULES.union(additional_modules)
        self.block_environment = block_environment
        self.block_globals = block_globals

        # Exceptions for allowed functions (must patch them yourself)
        self.dangerous_funcs = self.DANGEROUS_FUNCTIONS
        for func in allowed_functions:
            try:
                self.dangerous_funcs.pop(func)
            except KeyError:
                continue
        
        # Safe builtins (exclude dangerous ones like eval, exec, etc.)
        self.allowed_builtins = {
            'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray',
            'bytes', 'callable', 'chr', 'classmethod', 'delattr', 'dict',
            'dir', 'divmod', 'enumerate', 'filter', 'float', 'format',
            'frozenset', 'getattr', 'hasattr', 'hash', 'hex', 'id',
            'input', 'int', 'isinstance', 'issubclass', 'iter', 'len',
            'list', 'locals', 'map', 'max', 'memoryview', 'min', 'next',
            'object', 'oct', 'ord', 'pow', 'print', 'property', 'range',
            'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
            'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple',
            'type', 'vars', 'zip',
        }.union(additional_builtins)
    
    def __call__(self, test_class):
        """Apply patches to all test methods in the class."""
        original_setup = test_class.setUp if hasattr(test_class, 'setUp') else None
        original_teardown = test_class.tearDown if hasattr(test_class, 'tearDown') else None
        decorator_self = self
        def new_setup(self):
            # First call original setUp if it exists (i.e. setUp is exempt from patching, to allow mock_open(), etc)
            if original_setup:
                original_setup(self)
            
            """Initialize the security patches."""
            self._patch_stack = ExitStack()
            self._patch_stack.__enter__()

            # Patch dangerous functions
            for func_path, error in decorator_self.dangerous_funcs.items():
                mock = MagicMock(side_effect=error)
                self._patch_stack.enter_context(patch(func_path, mock))
            
            # Block environment variables
            if decorator_self.block_environment:
                self._patch_stack.enter_context(
                    patch.dict('os.environ', {}, clear=True)
                )
            
            # Replace __import__ with safe version
            original_import = __builtins__['__import__'] if isinstance(__builtins__, dict) else __builtins__.__import__
            
            def safe_import(name, *args, **kwargs):
                module_base = name.split('.')[0]
                if module_base not in decorator_self.allowed_modules:
                    raise ModuleNotFoundError(
                        f"No module named '{module_base}'."
                        # f"Allowed: {sorted(decorator_self.allowed_modules)}"
                    )
                return original_import(name, *args, **kwargs)
            
            self._patch_stack.enter_context(
                patch('builtins.__import__', safe_import)
            )
            
            # Remove dangerous builtins
            dangerous_builtins = {
                'eval', 'exec', 'compile', '__import__',
                'breakpoint', 'globals', 'locals',
            }
            
            for builtin_name in dangerous_builtins:
                if builtin_name in __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__:
                    if builtin_name == '__import__': continue # since import is handled in safe_import
                    self._patch_stack.enter_context(
                        patch.dict(
                            'builtins.__dict__', 
                            {
                                builtin_name: MagicMock(side_effect=PermissionError(f"'{builtin_name}' is not allowed"))
                            },
                            clear=False
                        )
                    )
        
        def new_teardown(self):
            """Clean up patches."""
            if hasattr(self, '_patch_stack'):
                self._patch_stack.__exit__(None, None, None)
            
            # Call original tearDown if it exists
            if original_teardown:
                original_teardown(self)
        
        test_class.setUp = new_setup
        test_class.tearDown = new_teardown
        
        return test_class

class SecureTestWithFileOpen(SecureTest):
    """\
    SecureTest but also with builtins.open unpatched
    
    Note that all unpatched functions/modules are the sole responisibilty of the implementor to ensure that they are patched
    """
    def __init__(self, additional_modules: list[str] = [], additional_builtins: list[str] = [], allowed_functions: list[str] = [], block_environment: bool = True, block_globals: bool = True):
        super().__init__(additional_modules, additional_builtins+['open'], allowed_functions+['builtins.open'], block_environment, block_globals)