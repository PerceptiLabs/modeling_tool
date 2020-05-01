import ast
from collections import namedtuple

from code_generator.base import CodeGenerator

LayerDescr = namedtuple('LayerDescr', ['name', 'code', 'input_layers', 'layer_type'])
ImportDescr = namedtuple('ImportDescr', ['module_name', 'as_name'])


class ScriptBuilder:
    def __init__(self):
        self._layers = []
        self._imports = []
        self._statements = []

    def layer(self, layer_name, layer_code, input_layers=None, checkpoint=None, layer_type=''):
        ast.parse(layer_code)

        if any([layer_name == x.name for x in self._layers]):
            raise ValueError("A layer with name {} already exists!".format(layer_name))
        
        new_layer_code = 'def func_{layer_name}(layer_name, X):\n'.format(layer_name=layer_name)
        new_layer_code += '    Y = None\n' # TODO: REMOVE??? 
        
        split = [line for line in layer_code.split('\n') if line != ''] # TODO: expand ; newline?
        for line in split:
            new_layer_code += '    ' + line + '\n'


        new_layer_code += '    api.data.store_locals(locals())\n' # TODO: REMOVE???

        new_layer_code += '    return Y\n'


        # TODO: these replaces shouldnt exist in later versions, but needed for now.
        new_layer_code = new_layer_code.replace('api.data.store(', 'api.override_layer_id(layer_name, api.data.store)(')
        new_layer_code = new_layer_code.replace('api.data.stack(', 'api.override_layer_id(layer_name, api.data.stack)(')
        new_layer_code = new_layer_code.replace('api.data.store_locals(', 'api.override_layer_id(layer_name, api.data.store_locals)(')
        new_layer_code = new_layer_code.replace('api.cache.put(', 'api.override_layer_id(layer_name, api.cache.put)(')                        
        new_layer_code = new_layer_code.replace('global state_tensor, env', 'global state_tensor, env, history_length')
        
        descr = LayerDescr(layer_name, new_layer_code, input_layers, layer_type)
        self._layers.append(descr)

    def statement(self, code: str):
        ast.parse(code)
        self._statements.append(code)                

    def global_import(self, module: str, as_name: str=None):
        self._imports.append(ImportDescr(module, as_name))

    def build_to_file(self):
        pass

    def build_imports(self) -> str:
        code = ''

        # --- Build preamble (imports, custom statements)
        for imp in self._imports:
            if imp.as_name is None:
                code += 'import {}\n'.format(imp.module_name)
            else:
                code += 'import {} as {}\n'.format(imp.module_name, imp.as_name)
        code += '\n'

        for stmt in self._statements:
            code += stmt
            code += '\n'
        code += '\n'

        return code

    def build_runscript(self) -> str:
        code = ''
        
        code += 'if True:\n'
        for layer in self._layers:
            code += '    # {}\n'.format(layer.layer_type)
            if len(layer.input_layers) == 0:
                code += '    X = None\n'
            elif len(layer.input_layers) == 1:
                code += '    X = {"Y": Y_%s}\n' % layer.input_layers[0]
            else:
                code += '    X = {}\n'
                for input_layer in layer.input_layers:
                    code += '    X["%s"] = {"Y": Y_%s}\n' % (input_layer, input_layer)

            code += '    Y_{layer_name} = func_{layer_name}("{layer_name}", X)\n'.format(layer_name=layer.name)             
            code += '\n' 

        return code

    def build(self) -> str:
        code = ''

        code += self.build_imports()

        # --- Add the layer functions.
        for layer in self._layers:
            code += layer.code
            code += '\n'

        # --- Add the execution sequence of the layers
        code += '\n'
        #code += 'if __name__ == "__main__":\n' # not running from main if exec..

        code += self.build_runscript()           
            
        return code
    
        
        
        

        


        
        
        
        
        
        
        
        

    
