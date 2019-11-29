import ast
from collections import namedtuple

from code_generator.base import CodeGenerator

LayerDescr = namedtuple('LayerDescr', ['name', 'code', 'input_layers', 'layer_type'])
ImportDescr = namedtuple('ImportDescr', ['module_name', 'as_name'])


class ScriptBuilder:
    def __init__(self):
        self._layers = []
        self._imports = []

    def layer(self, layer_name, layer_code, input_layers=None, checkpoint=None, layer_type=''):
        ast.parse(layer_code)

        assert layer_type != ''
        
        if any([layer_name == x.name for x in self._layers]):
            raise ValueError("A layer with name {} already exists!".format(layer_name))


        new_layer_code  = 'class Wrapper{layer_name}:\n'.format(layer_name=layer_name)
        new_layer_code += '    def __init__(self):\n'
        new_layer_code += '        self._locals = {}\n'
        new_layer_code += '        self._n_calls = 0\n'
        
        new_layer_code += '    def __call__(self, layer_name, X):\n'
        new_layer_code += '        Y = None\n' # TODO: REMOVE??? 
        
        split = [line for line in layer_code.split('\n') if line != ''] # TODO: expand ; newline?
        for line in split:
            new_layer_code += '        ' + line + '\n'


        #new_layer_code += '        api.data.store_locals(locals())\n' # TODO: REMOVE???

        new_layer_code += '        locals_ = locals()\n'

        new_layer_code += '        if self._n_calls > 0:\n'
        new_layer_code += '            locals_ = {"%s/replica_%d" % (k, self._n_calls) : v \n'
        new_layer_code += '                       for k, v in locals_.items()}\n'
        new_layer_code += '        self._locals = locals_\n'

        new_layer_code += '        print("aa", repr(self),self._n_calls, locals_.keys())\n'        
        new_layer_code += '        self._n_calls += 1\n'

        if layer_type != 'DataData':
            new_layer_code += '        return Y\n'
        else:
            new_layer_code += '        return (X_train_copy, X_validation_copy, X_test_copy)\n'

        # TODO: these replaces shouldnt exist in later versions, but needed for now.
        new_layer_code = new_layer_code.replace('X_train = tf.data.Dataset', 'X_train = X_train_copy = tf.data.Dataset')
        new_layer_code = new_layer_code.replace('X_validation = tf.data.Dataset', 'X_validation = X_validation_copy = tf.data.Dataset')
        new_layer_code = new_layer_code.replace('X_test = tf.data.Dataset', 'X_test = X_test_copy = tf.data.Dataset')        
        new_layer_code = new_layer_code.replace('api.data.store(', 'api.override_layer_id(layer_name, api.data.store)(')
        new_layer_code = new_layer_code.replace('api.data.stack(', 'api.override_layer_id(layer_name, api.data.stack)(')
        new_layer_code = new_layer_code.replace('api.data.store_locals(locals())', 'api.override_layer_id(layer_name, api.data.store_locals)({k:v for k, v in locals().items() if k != "X"})')
        new_layer_code = new_layer_code.replace('api.cache.put(', 'api.override_layer_id(layer_name, api.cache.put)(')                        
        new_layer_code = new_layer_code.replace('global state_tensor, env', 'global state_tensor, env, history_length')

        # Remove iterators
        if layer_type == 'DataData':        
            new_layer_code = new_layer_code.replace('train_iterator = iterator.make_initializer', '#train_iterator = iterator.make_initializer')
            new_layer_code = new_layer_code.replace('validation_iterator = iterator.make_initializer', '#validation_iterator = iterator.make_initializer')
            new_layer_code = new_layer_code.replace('test_iterator = iterator.make_initializer', '#test_iterator = iterator.make_initializer')        
            new_layer_code = new_layer_code.replace('iterator = tf.data.Iterator.from_structure', '#iterator = tf.data.Iterator.from_structure')
            new_layer_code = new_layer_code.replace('Y = next_elements = iterator.get_next()', '#Y = next_elements = iterator.get_next()')
        
        descr = LayerDescr(layer_name, new_layer_code, input_layers, layer_type)
        self._layers.append(descr)

    def build(self) -> str:
        code = ''

        # --- Add the layer functions.
        for layer in self._layers:
            code += layer.code
            code += '\n'

        # --- Add the execution sequence of the layers
        
        code += '\n'
        #code += 'if __name__ == "__main__":\n' # not running from main if exec..

        assert self._layers[0].layer_type == 'DataData' and self._layers[1].layer_type == 'DataData'
        assert self._layers[-1].layer_type == 'TrainNormal'

        code += 'datasets = {}\n'
        code += 'datasets["{layer_name}"] = Wrapper{layer_name}()\n'.format(layer_name=self._layers[0].name)
        code += 'datasets["{layer_name}"] = Wrapper{layer_name}()\n'.format(layer_name=self._layers[1].name)
        code += '\n'
        code += 'layer_calls = []\n'

        for layer in self._layers[2:-1]: # Skip data and training layers (see asserts above)
            id_ = layer.name

            names = ['"' + x +'"' for x in layer.input_layers]
            args = '[' + ', '.join(names) + ']'
            code += 'layer_calls.append({"layer_id": "%s", "wrapper": Wrapper%s(), "input_layers": %s})\n' % (id_, id_, args)
        
        code += '\n'

        # training layer
        code += 'X = {"datasets": datasets, "layer_calls": layer_calls}\n'
        code += 'Wrapper{layer_name}()("{layer_name}", X)\n'.format(layer_name=self._layers[-1].name)
            
        print(code)
        #import pdb;pdb.set_trace()
            
        return code
    
        
        
        

        


        
        
        
        
        
        
        
        

    
