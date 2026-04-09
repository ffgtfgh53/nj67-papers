import sys
import warnings

from typing import Any
from RestrictedPython import PrintCollector, compile_restricted
from RestrictedPython.Guards import safe_builtins

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

def load_user_functions(
    user_code_string: str, 
    allowed_function_names: list[str] | None = None, 
    block_print: bool = True, 
    custom_globals: dict[str, Any] = {}):
    """
    Safely load functions from user-provided code.
    
    Args:
        user_code_string: The user's Python code as a string
        allowed_function_names: List of function names to allow (whitelist)
        block_print: Whether print statements should be blocked from printing to stdout
        custom_globals: Custom globals for builtins (e.g. to patch certain functions like builtins.open)
    
    Returns:
        dict of allowed functions

    Example:

        ```
        user_code = '''
        def neighbour():
            print("Hey neighbour!")

        def task1_67():
            print("Hi from task1_67")
            neighbour()

        def task67_1():
            print("Hi from task67_1")
        '''
        funcs = load_user_functions(user_code, ['task1_67'], block_print=False)
        output = funcs['task1_67']() # Prints "Hi from task1_67" and "Hey neighbour!"

        funcs['print']("Hello World!") # Fails
        ```
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
            mode='exec'
        )
    
    # Check for compilation errors
    if getattr(compiled, 'errors', None):
        raise SyntaxError(f"Code compilation failed: {compiled.errors}")
    
    # Create a restricted execution environment
    safe_globals = {
        '__builtins__': safe_builtins,
        '__name__': '__main__',
        '__metaclass__': type,
        '_getiter_': iter,
        '_iter_unpack_sequence_': iter,
        '_write_': lambda x: x,  # Allow writing to variables
        '_apply_': lambda f: f,  # Allow function calls
        '_print_': PrintCollector if block_print else StdoutPrintCollector,
        '_getattr': getattr,
    }

    safe_globals.update(custom_globals)
    original_safe_globals = safe_globals.copy()
    
    # Execute the user code
    try:
        exec(compiled, safe_globals)
    except Exception as e:
        raise RuntimeError(f"Error executing user code: {e}")
    
    # Extract only needed functions
    extracted_functions = {}
    
    for name, obj in safe_globals.items():
        # Skip given functions
        if name in original_safe_globals:
            continue

        # Skip private/magic attributes
        if name.startswith('_'):
            continue
        
        # Only extract functions and classes
        if not callable(obj) and not isinstance(obj, type):
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
