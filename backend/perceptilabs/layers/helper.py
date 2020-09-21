import ast
import logging
import importlib

from perceptilabs.utils import add_line_numbering
from perceptilabs.logconf import APPLICATION_LOGGER


logger = logging.getLogger(APPLICATION_LOGGER)


class _CodeLoader:
    """ Data package module loader. Executes package import code and adds the package to the
    module cache.
    """
    def __init__(self, source_code):
        self._source_bytes = source_code.encode()

    @classmethod
    def create_module(cls, spec):  
        return None

    def exec_module(self, module, tag=None):
        if tag is None:
            file_name = '<rendered-code>'
        else:
            file_name = f'<rendered-code: {tag}>'
            
        code_obj = compile(self._source_bytes, file_name, 'exec', dont_inherit=True, optimize=2)
        exec(code_obj, module.__dict__)


class LayerHelper:
    def __init__(self, script_factory, layer_spec, graph_spec=None):
        self._script_factory = script_factory
        self._layer_spec = layer_spec
        self._graph_spec = graph_spec
        self._class_object = None
        
    def get_code(self, preamble=None, prepend_imports=False, layer_code=True, check_syntax=False, print_code=False):
        code = preamble or ""
        
        if prepend_imports:
            stdlib, thirdparty, plabs = self._script_factory.get_layer_import_statements(
                self._layer_spec, include_top_level=True
            )
            for stmt in set.union(stdlib, thirdparty, plabs):
                code += stmt + '\n'            
            code += '\n'

        if layer_code:
            code += self._script_factory.render_layer_code(
                self._layer_spec,
                macro_kwargs={'layer_spec': self._layer_spec, 'graph_spec': self._graph_spec}
            )
        
        if check_syntax:
            try:
                ast.parse(code)
            except SyntaxError:
                logger.error('Syntax error in:\n' + add_line_numbering(code))
                raise

        if print_code:
            print(f'{self._layer_spec.id_} [{self._layer_spec.type_}] code:\n' + add_line_numbering(code))
        return code

    def get_class(self, preamble=None, print_code=False):
        if self._class_object is None:
            code = self.get_code(
                prepend_imports=True, check_syntax=True, preamble=preamble, print_code=print_code
            )
            
            loader = _CodeLoader(code)
            spec = importlib.machinery.ModuleSpec("my_module", loader)
            module = importlib.util.module_from_spec(spec)
            try:        
                spec.loader.exec_module(module, tag=f'{self._layer_spec.id_} [{self._layer_spec.type_}]')        
            except:
                logger.exception('Error importing code:\n' + add_line_numbering(code))
                raise
        
            self._class_object = getattr(module, self._layer_spec.sanitized_name)        
        return self._class_object

    def get_instance(self, preamble=None, print_code=False):
        class_object = self.get_class(preamble=preamble, print_code=print_code)
        
        try:
            instance = class_object()
        except:
            logger.exception('Error running code:\n' + add_line_numbering(self.get_code(prepend_imports=True)))
            raise
        
        return instance

    def get_line_count(self, preamble=None, prepend_imports=False, layer_code=True):
        code = self.get_code(preamble=preamble, prepend_imports=prepend_imports, layer_code=layer_code)
        line_count = len(code.split('\n')) - int(len(code) > 0)
        return line_count
    
