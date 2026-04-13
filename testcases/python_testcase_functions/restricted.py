import ast
import sys
import warnings

from typing import Any
from RestrictedPython import PrintCollector, RestrictingNodeTransformer, compile_restricted, utility_builtins, limited_builtins
from RestrictedPython.Guards import guarded_iter_unpack_sequence, safe_builtins
from RestrictedPython.Eval import default_guarded_getattr, default_guarded_getiter, default_guarded_getitem

_SEAB_ALLOWED_MODULES = ['csv', 'datetime', 'math', 'random', 'sqlite3']
_EXTRA_ALLOWED_MODULES = ['string', 'statistics', 'json', 're']

class StdoutPrintCollector(PrintCollector):  
    """PrintCollector that writes to both stdout and internal buffer."""  
      
    def _call_print(self, *objects, **kwargs):  
        # Always write to stdout first  
        kwargs['file'] = sys.stdout  
        print(*objects, **kwargs)  
          
        # Also collect in internal buffer for 'printed' variable  
        if 'file' in kwargs:  
            del kwargs['file']  
        super()._call_print(*objects, **kwargs)

class SimpleImportTransformer(RestrictingNodeTransformer):
    # By AI
    def visit_Import(self, node): #type: ignore
        node = self.check_import_names(node)

        # Transform imports for modules available in utility_builtins  
        new_nodes = []  
        for alias in node.names: #type: ignore
            module_name = alias.name  
              
            # Check if this module is in utility_builtins  
            if module_name in _SEAB_ALLOWED_MODULES + _EXTRA_ALLOWED_MODULES:  
                # Transform: import math  
                # To: math = utility_builtins['math']  
                assign = ast.Assign(  
                    targets=[ast.Name(alias.asname or module_name, ast.Store())],  
                    value=ast.Subscript(  
                        value=ast.Name('utility_builtins', ast.Load()),  
                        slice=ast.Constant(module_name),  
                        ctx=ast.Load()  
                    )  
                )  
                new_nodes.append(ast.fix_missing_locations(assign))  
            else:  
                # For other modules, keep the original import (will fail at runtime)  
                new_nodes.append(node)  
        return new_nodes if len(new_nodes) == 1 else node  

# Source - https://stackoverflow.com/a/79607366
# Posted by Bill Rayner
# Retrieved 2026-04-13, License - CC BY-SA 4.0
# Honestly the documentation of RestrictedPython is starting to pmo

def _inplacevar_(op, var, expr):
    if op == "+=":
        return var + expr
    elif op == "-=":
        return var - expr
    elif op == "*=":
        return var * expr
    elif op == "/=":
        return var / expr
    elif op == "%=":
        return var % expr
    elif op == "**=":
        return var ** expr
    elif op == "<<=":
        return var << expr
    elif op == ">>=":
        return var >> expr
    elif op == "|=":
        return var | expr
    elif op == "^=":
        return var ^ expr
    elif op == "&=":
        return var & expr
    elif op == "//=":
        return var // expr
    elif op == "@=":
        return var // expr


def load_user_functions(
    user_code_string: str, 
    allowed_function_names: list[str] | None = None, 
    block_print: bool = True, 
    custom_globals: dict[str, Any] = {},
    extra_imports: dict[str, Any] = {},
    ):
    """
    Safely load functions from user-provided code.
    
    Args:
        user_code_string: The user's Python code as a string
        allowed_function_names: List of function names to allow (whitelist)
        block_print: Whether print statements should be blocked from printing to stdout
        custom_globals: Custom globals for builtins (e.g. to patch certain functions like builtins.open)
    
    Returns:
        dict of allowed functions {'name': func}

    Example:

        ```
        user_code = textwrap.dedent('''
            def neighbour():
                print("Hey neighbour!")

            def task1_67():
                print("Hi from task1_67")
                neighbour()

            def task67_1():
                print("Hi from task67_1")
        ''')
        funcs = load_user_functions(user_code, ['task1_67'], block_print=False)
        _return_val = funcs['task1_67']() # Prints "Hi from task1_67" and "Hey neighbour!"

        funcs_noprint = load_user_functions(user_code, ['task1_67'], block_print=True)
        _return_val = funcs_noprint['task1_67'] # Does not print anything

        funcs['print']("Hello World!") # Fails
        ```

    Useful features:
        block_print=False to print to stdout so you can mock a sys.stdout object with unittest.mock
    """
    
    # Compile the user code with restrictions
    with warnings.catch_warnings():  
        warnings.filterwarnings( # Not applicable since we redirect all printing to stdout using StdoutPrintCollector
            'ignore',   
            message=r".*Prints, but never reads 'printed' variable.$",  #regex
            category=SyntaxWarning
        )
        compiled = compile_restricted(
            user_code_string,
            filename='<user_code>',
            mode='exec',
            policy=SimpleImportTransformer
        )
    
    # Check for compilation errors
    if getattr(compiled, 'errors', None):
        raise SyntaxError(f"Code compilation failed: {compiled.errors}")
    
    # Create a restricted execution environment
    safe_globals = {
        '__builtins__': safe_builtins,
        '__name__': '__main__',
        '__metaclass__': type,
        '_getiter_': default_guarded_getiter,
        '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
        '_write_': lambda x: x,  # Allow writing to variables
        '_apply_': lambda f: f,  # Allow function calls
        '_print_': PrintCollector if block_print else StdoutPrintCollector,
        '_getattr_': default_guarded_getattr,
        '_getitem_': default_guarded_getitem,
        '_inplacevar_': _inplacevar_, # In-place operations
        # For imports
        'utility_builtins': utility_builtins | extra_imports,
        # Types
        # (man idk why RestrictedPython forbids creation of lists/tuples from str)
        # (also range is limited in size but they have plenty of other ways to slow down execution (like while True))
        'set': set,
        'frozenset': frozenset,
        'list': list,
        'tuple': tuple,
        'range': range,
        'sum': sum,
    }

    globals_context = safe_globals | custom_globals
    original_globals_context = globals_context.copy()
    
    # Execute the user code
    try:
        exec(compiled, globals_context)
    except Exception as e:
        raise RuntimeError(f"Error executing user code: {e}")
    
    # Extract only needed functions
    extracted_functions = {}
    
    for name, obj in globals_context.items():
        # Skip given functions
        if name in original_globals_context:
            continue

        # Skip private/magic attributes
        if name.startswith('_'):
            continue
        
        # Only extract functions and classes
        if not ( callable(obj) or isinstance(obj, type) ):
            continue
        
        # If whitelist provided, check against it
        if allowed_function_names and name not in allowed_function_names:
            continue
        
        extracted_functions[name] = obj
    
    return extracted_functions

# Example usage
if __name__ == "__main__":
    user_code = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def dangerous_function():
    # This will fail in restricted environment
    # exec("print('hehe malicious')")
    pass

class Banana():
    "A banana with type"
    def __init__(self, type):
        self.type = type

def extra():
    print('hi i am extra')
    print(Banana('hi').type)
    
malicious_var = "This will be filtered"
"""

    try:
        # Load only specific functions
        functions: dict[str, Any] = load_user_functions(
            user_code,
            allowed_function_names=['add', 'multiply', 'extra', 'Banana'],
            block_print=False
        )
        
        print("Loaded functions:", list(functions.keys()))
        print("Result of add:", functions['add'](5, 3))
        print("Result of multiply:", functions['multiply'](5, 3))
        functions['extra']()
        
    except Exception as e:
        print(f"Error running code: {e.__class__.__name__}: {e}")
