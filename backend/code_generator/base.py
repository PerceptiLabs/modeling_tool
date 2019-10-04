import copy
from abc import ABC, abstractmethod
from collections import namedtuple

CodePart = namedtuple('CodePart', ['name', 'code'])

class CodeGenerator(ABC):
    @abstractmethod
    def get_code(self, mode='normal'):
        raise NotImplementedError

    def get_code_parts(self):
        code = self.get_code()        
        code_parts = [CodePart(name=None, code=code)]
        return code_parts

    
class CustomCodeGenerator(CodeGenerator):
    def __init__(self, input_):
        if isinstance(input_, str):
            self._code_parts = [CodePart(name=None, code=input_)]
        elif isinstance(input_, list) and all([isinstance(x, CodePart) for x in input_]):
            self._code_parts = copy.copy(input_)
        else:
            raise ValueError("Inputs must be either string or list of CodeParts")

    def get_code_parts(self, mode='normal'):
        return self._code_parts

    def get_code(self, mode='normal'):    
        code = ''
        for cp in self._code_parts:
            code += cp.code + '\n'            
        return code

