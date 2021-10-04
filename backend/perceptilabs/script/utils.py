import os
import copy
import importlib
import pkg_resources
from tempfile import NamedTemporaryFile

from perceptilabs.utils import add_line_numbering
from perceptilabs.layers import get_layer_builder

_RENDER_MACRO_TEMPLATE = \
"""
{{% from "{macro_file}" import {macro_name} %}}
{{{{ {macro_name}({arg_str})}}}}
"""

def create_macro_loader(macro_file, macro_name, macro_parameters):
    """ Creates a Jinja2 template for loading a macro """
    
    _macro_params = {}    
    for arg_name, arg_value in macro_parameters.items():        
        if isinstance(arg_value, str):
            arg_value = f"'{arg_value}'"
        _macro_params[arg_name] = arg_value        
    arg_str = ', '.join(f"{arg_name}={arg_value}" for arg_name, arg_value in _macro_params.items())
    
    template = _RENDER_MACRO_TEMPLATE.format(
        macro_file=macro_file,
        macro_name=macro_name,
        arg_str=arg_str
    ).strip()

    return template


def render_and_execute_macro(j2_engine, macro_file, macro_name, macro_parameters, import_statements=None):
    template = create_macro_loader(macro_file, macro_name, macro_parameters)

    code = 'import logging\n'
    if import_statements:
        code += '\n'.join(import_statements or [])
        code += '\n\n'
    code += 'log = logging.getLogger(__name__)\n\n'        
    code += j2_engine.render_string(template)

    
    is_unix = os.name != 'nt' # Windows has permission issues when deleting tempfiles
    with NamedTemporaryFile('wt', delete=is_unix, suffix='.py') as f:
        f.write(code)
        f.flush()

        spec = importlib.util.spec_from_file_location("my_module", f.name)        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
    if not is_unix:
        os.remove(f.name)

    return module, code


class MyLoader:
    """ Data package module loader. Executes package import code and adds the package to the
    module cache.
    """
    def __init__(self, source_code):
        self._source_bytes = source_code.encode()

    @classmethod
    def create_module(cls, spec):  
        return None

    def exec_module(self, module):
        file_name = '<rendered-code>'
        code_obj = compile(self._source_bytes, file_name, 'exec', dont_inherit=True, optimize=2)
        exec(code_obj, module.__dict__)


def import_code(code):
    loader = MyLoader(code)
    spec = importlib.machinery.ModuleSpec("my_module", loader)
    module = importlib.util.module_from_spec(spec)
    try:        
        spec.loader.exec_module(module)        
    except:
        print(add_line_numbering(code))
        raise
    return module


