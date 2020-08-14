import os
import copy
import importlib
import pkg_resources
from tempfile import NamedTemporaryFile

from perceptilabs.utils import add_line_numbering
from perceptilabs.layers import get_layer_builder
from perceptilabs.core_new.layers.definitions import TEMPLATES_DIRECTORY

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


def instantiate_layer_from_macro(j2_engine, macro_file, macro_name, macro_parameters, import_statements=None):
    assert 'layer_name' in macro_parameters
    
    module, _ = render_and_execute_macro(j2_engine, macro_file, macro_name, macro_parameters, import_statements)
    
    class_object = getattr(module, macro_parameters['layer_name'])
    instance = class_object()

    return instance    
    

def create_layer(j2_engine, definition_table, top_level_imports, layer_type, **macro_parameters):
    layer_def = definition_table.get(layer_type)

    if 'layer_name' not in macro_parameters:
        macro_parameters['layer_name'] = layer_type


    import_statements = layer_def.import_statements + top_level_imports

    layer = instantiate_layer_from_macro(
        j2_engine,
        layer_def.template_file, layer_def.template_macro,
        macro_parameters,
        import_statements
    )
    
    return layer



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


def render_macro(engine, macro_path, macro_name, macro_parameters=None, renderer_kwargs=None, import_statements=None):
    renderer_kwargs = renderer_kwargs or {}

    if not os.path.isfile(macro_path):
        templates_directory = pkg_resources.resource_filename('perceptilabs', TEMPLATES_DIRECTORY)
        _macro_path = os.path.join(templates_directory, macro_path)

        if os.path.isfile(_macro_path):
            macro_path = _macro_path
        else:
            raise ValueError(f"Couldn't locate macro {macro_path}. Used directory '.' and '{templates_directory}'")        

    
    template = "import logging\n"

    if import_statements:
        template += "\n".join(import_statements or [])
        template += "\n\n"

    template += "log = logging.getLogger(__name__)\n"
    template += "\n"

    with open(macro_path, 'r') as f:
        template += f.read()
        template += "\n\n"

    macro_parameters = macro_parameters or {}
    arg_str = ', '.join(f"{arg_name}={arg_value}" for arg_name, arg_value in macro_parameters.items())        
    template += "{{" + f"{macro_name}({arg_str})" + "}}\n"

    code = engine.render_string(template, **renderer_kwargs)
    return code


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


def run_and_get_layer_macro(j2_engine, definition_table, macro_path, macro_name, layer_type, parameters, import_statements):
    layer_def = definition_table.get(layer_type)    
    import_statements = layer_def.import_statements + import_statements
    
    builder = get_layer_builder(layer_type)
    
    # Default parameters
    builder.set_parameter('id', layer_type)
    builder.set_parameter('name', layer_type)    
    builder.set_parameter('type', layer_type)
    builder.set_parameter('code', None)
    builder.set_parameter('visited', False)
    builder.set_parameter('end_points', [])
    builder.set_parameter('checkpoint_path', None)
    builder.set_parameter('backward_connections', ())
    builder.set_parameter('forward_connections', ())                            

    # Set parameters
    for key, value in parameters.items():
        builder.set_parameter(key, value)
    layer_spec = builder.build()
    
    code = render_macro(
        j2_engine,
        macro_path,
        macro_name,
        macro_parameters={'layer_name': f"'{layer_spec.name}'", 'layer_spec': 'spec_obj'},
        renderer_kwargs={'spec_obj': layer_spec},
        import_statements=import_statements
    )
    module = import_code(code)

    class_object = getattr(module, layer_spec.name)
    instance = class_object()
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
