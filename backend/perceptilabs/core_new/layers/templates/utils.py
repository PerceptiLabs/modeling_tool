import os
import copy
import importlib
from tempfile import NamedTemporaryFile
    
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


def instantiate_layer_from_macro(j2_engine, macro_file, macro_name, macro_parameters, import_statements=None):
    assert 'layer_name' in macro_parameters
    
    template = create_macro_loader(macro_file, macro_name, macro_parameters)

    code = ''
    if import_statements:
        code += '\n'.join(import_statements or [])
        code += '\n\n'        
    code += j2_engine.render_string(template)
    
    is_unix = os.name != 'nt' # Windows has permission issues when deleting tempfiles
    with NamedTemporaryFile('wt', delete=is_unix, suffix='.py') as f:
        f.write(code)
        f.flush()
            
        spec = importlib.util.spec_from_file_location("my_module", f.name)        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        class_object = getattr(module, macro_parameters['layer_name'])
        instance = class_object()

    if not is_unix:
        os.remove(f.name)

    return instance    
    

    


if __name__ == "__main__":
    import pkg_resources

    from perceptilabs.core_new.layers.templates.base import J2Engine
    from perceptilabs.core_new.layers.definitions import TEMPLATES_DIRECTORY

    templates_directory = pkg_resources.resource_filename('perceptilabs', TEMPLATES_DIRECTORY)
    j2_engine = J2Engine(templates_directory)

    macro_parameters = {
        'layer_name': 'MyLayer'
    }

    import_statements = [
        'import tensorflow as tf',
        'from typing import Dict',
        'from perceptilabs.core_new.utils import Picklable',
        'from perceptilabs.core_new.layers.base import Tf1xLayer'
    ]
    
    instance = instantiate_layer_from_macro(
        j2_engine,
        'tf1x.j2',
        'layer_tf1x_grayscale',
        macro_parameters,
        import_statements
    )
    

    import pdb; pdb.set_trace()
